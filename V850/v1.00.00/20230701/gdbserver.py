# GDBSERVER on CubeSuite+'s Python Console (for Renesas V850 Simulator)
# coding=utf-8

#       Created on: Apr 29, 2012
# Last Modified on: Apr 29, 2012
#           Author: MON-80
#          License: MIT

# USAGE:
# 起動方法(必要に応じてパスを付加する必要があります)
#   (1) CubeSuite+.exe /ps gdbserver.py プロジェクトファイル名.mtpj
#       CPU使用率が100%に張り付く問題があります
#       動的に自分自身のスクリプト内の関数/変数の定義をアップデートすることが出来ません
#   (2) CubeSuiteW+.exe /ps gdbserver.py プロジェクトファイル名.mtpj
#       CPU使用率が100%に張り付く問題があります
#       動的に自分自身のスクリプト内の関数/変数の定義をアップデートすることが出来ません
#   (3) CubeSuiteW+.exe プロジェクトファイル名.mtpj
#       以下の内容でプロジェクトファイル名.pyというスクリプトファイルを作成しておきます
#       common.Source("gdbserver.py")
#       なお、この内容にパスを付加する場合、以下の2通りの表記方法があります
#       (例)
#       common.Source(r"E:\tools\micom\Renesas\e2-P-Helios\workspace\Python\gdbserver.py")
#       common.Source("E:/tools/micom/Renesas/e2-P-Helios/workspace/Python\gdbserver.py")
#       CPU使用率が100%に張り付く問題はありません
#       動的に自分自身のスクリプト内の関数/変数の定義をアップデートすることが出来ます
# モニタコマンド
#   monitor python_statement
#     Pythonの文を実行します
#   monitor eval(python_expression)
#     Pythonの式を評価します
#   monitor reset
#     CubeSuite+のデバッグツール上でCPUをリセットします
#   monitor load ファイル名.hex
#     CubeSuite+のデバッグツール上でHEXファイルをダウンロードします
#     CubeSuite+がHEXファイルと認識するものであればファイルの拡張子は何でも構いません
#   monitor debug = 0(デフォルト)/1
#     debug = 0 : Pythonコンソール上に詳細なデバッグメッセージを表示しません(少しは表示されます)
#     debug = 1 : Pythonコンソール上に詳細なデバッグメッセージを表示します
#   monitor fixme = 0/1(デフォルト)
#     fixme = 0 : 不具合の対症療法的な対処を無効にします
#     fixme = 1 : 不具合の対症療法的な対処を有効にします
#   monitor quit = 0(デフォルト)/1/2/3/4
#     quit = 0 : GDB終了時にGDBSERVERスクリプトを終了しません(デバッグツールも切断しません)
#     quit = 1 : GDB終了時にGDBSERVERスクリプトを終了しません(デバッグツールは切断します)
#     quit = 2 : GDB終了時にGDBSERVERスクリプトを終了します(デバッグツールは切断しません)
#     quit = 3 : GDB終了時にGDBSERVERスクリプトを終了します(デバッグツールも切断します)
#     quit = 4 : GDB終了時にCubeSuite+も終了します
# 
# FIXME:
# メモリライトがタイムアウトすることがある。対症療法的に対処したが、適切な方法は???
# ステップ実行を中断した時にGDBがエラーを表示することがある。^Cの有無の先読みが必要か???
#
# TODO:
# ブレーク時にPC以外にSP(R3),FP(R29),LP(R31)のレジスタ情報を返す
# ブレーク時にWatchpointブレークの情報を返したいがCubeSuite+固有のPythonオブジェクトでは不可能
# 適切なエラーをGDBへ返したいがGDBのエラーコードを調べないと返せない
# メモリリードライトの効率化(常に1バイトづつ処理するやり方は効率が良くない)
# CubeSuite+の起動オプション/psでスクリプトを指定するとCPU使用率が100％に張り付く問題の回避
# CubeSuite+固有のPythonオブジェクトのメッセージ出力を抑止する方法はないだろうか?
# CubeSuite+固有のPythonオブジェクトの取得出来ないメッセージ出力を取得する方法はないだろうか?
# 長時間使用時の動作の安定性はどうだろうか?
#
# MEMO
# CubeSuiteW+.exe プロジェクトファイル名.mtpj の場合は プロジェクトファイル名.py が実行される
# CubeSuite+.exe プロジェクトファイル名.mtpj の場合は プロジェクトファイル名.py が実行されない
# debugger.Memory.Read()の戻り値はUInt32型。debugger.Register.GetValue()の戻り値はstr型。

import socket, StringIO

HOST = "localhost"
PORT = 2159

debug = 0
fixme = 1
quit = 0

MODULE = str(sys.modules["__main__"])
SCRIPT = MODULE[MODULE.find(" from ")+7:-2]
VERSION = "v1.00.00.00"

MaxRecvPacket = 4096
MaxExceptRetry = 100
LastPacketData = ""

def Recv():
    global conn
    try:
        data = conn.recv(MaxRecvPacket)
    except:
        if debug > 0: print "DEBUG: exception @ data = conn.recv()"
        raise
    if debug > 0: print "RECV:", repr(data)
    return data

def Send(data):
    global conn
    try:
        conn.send(data)
    except:
        if debug > 0: print "DEBUG: exception @ conn.send()"
        raise
    if debug > 0: print "SEND:", repr(data)
    return

# Send Ack ('+' or '-') only
def SendAck(ack):
    Send(ack)
    return

# Send Packet ('$' + Reply or Empty + '#' + checksum)
def SendPacket(rep):
    global LastPacketData
    LastPacketData = "$" + rep + "#" + format(CalcChecksum(rep), "02x")
    Send(LastPacketData)
    return

# Send last Packet ('$' + Reply or Empty + '#' + checksum) again
def SendLastPacketAgain():
    global LastPacketData
    Send(LastPacketData)
    return

def CalcChecksum(str):
    sum = 0
    for i in range(len(str)):
        sum += ord(str[i])
    return sum % 256

# Note: High byte first
def HexStrToVal(str, sep, f = False):
    val= 0
    for i in range(len(str)):
        if str[i] == sep:
            break
        try:
            val = val * 16 + int(str[i], 16)
        except:
            break
    if f == False:
        return val
    else:
        return val, i

# Note: Low byte first
def ValToHexData(val, col = 8):
    hex = ""
    for i in range(0, col, 2):
        hex += format((val / (1 << (4 * i))) % 256, "02x")
    return hex

# Note: Low byte first
def HexDataToVal(hex):
    val = 0
    for i in range(0, len(hex), 2):
        try:
            val += (1 << (4 * i)) * int(hex[i:i+2], 16)
        except:
            pass
    return val

RegName = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", \
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23", "r24", "r25", "r26", "r27", "r28", "r29", "r30", "r31", \
    "eipc", "eipsw", "fepc", "fepsw", "ecr", "psw", "", "", "", "", "", "", "", "", "", "", \
    "ctpc", "ctpsw", "dbpc", "dbpsw", "ctbp", "", "", "", "", "", "", "", "", "", "", "", \
    "pc", "r29"]

def RegGetVal_(reg):
    if reg == "":
        return 0
    if debug > 0: print "debugger.Register.GetValue() : Reg =", reg, ", Val = "
    try:
        val = int(debugger.Register.GetValue(reg), 16)
    except:
        val = 0
    return val

def RegSetVal_(reg, val):
    if reg == "":
        return
    if debug > 0: print "debugger.Register.SetValue() : Reg =", reg, ", Val = 0x" + format(val, "08x")
    try:
        debugger.Register.SetValue(reg, val)
    except:
        pass
    return

# Note: Low byte first
def RegGetVal(reg):
    val = RegGetVal_(reg)
    return ValToHexData(val)

# Note: Low byte first
def RegSetVal(reg, val):
    RegSetVal_(reg, HexDataToVal(val))
    return "OK"

# Note: Low byte first
def RegGetValAll():
    ret = ""
    for reg in RegName:
        ret += RegGetVal(reg)
    return ret

def RegSetValPC(val):
    RegSetVal_("pc", val)
    return

# TODO: エラー発生時はどうする?
# TODO: 効率化(常に1バイトづつ処理するやり方は効率が良くない)
# Note: Low byte first
def MemGetVal(addr, leng):
    if debug > 0: print "debugger.Memory.Read() : Addr = 0x" + format(addr, "08x"), ", Len = 0x" + format(leng, "08x")
    ret = ""
    # addr, addr + lengの値のタンパプルーフは必要?
    for a in range(addr, addr + leng):
        val = 0
        try:
            val = int(debugger.Memory.Read(a, MemoryOption.Byte))
        except:
            pass
        ret += format(val, "02x")
    return ret

# TODO: エラー発生時はどうする?
# TODO: 効率化(常に1バイトづつ処理するやり方は効率が良くない)
# Note: Low byte first
def MemSetVal(addr, leng, data):
    if debug > 0: print "debugger.Memory.Write() : Addr = 0x" + format(addr, "08x"), ", Len = 0x" + format(leng, "08x")
    # addr, addr + lengの値のタンパプルーフは必要?
    for i in range(0, len(data), 2):
        try:
            debugger.Memory.Write(addr, int(data[i:i+2], 16), MemoryOption.Byte)
        except:
            pass
        addr += 1
    return "OK"

# ブレークポイントの管理にディクショナリ(連想配列)を使ってみる
BrkType = {}
BrkType["0"] = BreakType.Software
BrkType["1"] = BreakType.Hardware
BrkType["2"] = BreakType.Write
BrkType["3"] = BreakType.Read
BrkType["4"] = BreakType.Access
BrkCond = {}
BrkCond[BreakType.Software] = {}
BrkCond[BreakType.Hardware] = {}
BrkCond[BreakType.Write] = {}
BrkCond[BreakType.Read] = {}
BrkCond[BreakType.Access] = {}

def BrkClear():
    global BrkCond
    if debug > 0: print "debugger.Breakpoint.Delete()"
    debugger.Breakpoint.Delete()
    BrkCond[BreakType.Software] = {}
    BrkCond[BreakType.Hardware] = {}
    BrkCond[BreakType.Write] = {}
    BrkCond[BreakType.Read] = {}
    BrkCond[BreakType.Access] = {}
    return

# TODO: エラー発生時はどうする?
def BrkSetBp(addr, type):
    global ToolType, BrkType, BrkCond
    try:
        type = BrkType[type]
        if type == BreakType.Software and ToolType == DebugTool.Simulator:
            type = BreakType.Hardware
        num = debugger.Breakpoint.Set(BreakCondition(Address = addr, BreakType = type))
        if debug > 0: print "debugger.Breakpoint.Set(cond) : Num =", num, ", Addr = 0x" + format(addr, "08x")
        BrkCond[type][addr] = num
        if debug > 0: print "debugger.Breakpoint.Information()"
        if debug > 0: debugger.Breakpoint.Information()
    except:
        pass
    return "OK"

# TODO: エラー発生時はどうする?
def BrkDelBp(addr, type):
    global ToolType, BrkType, BrkCond
    try:
        type = BrkType[type]
        if type == BreakType.Software and ToolType == DebugTool.Simulator:
            type = BreakType.Hardware
        num = BrkCond[type][addr]
        debugger.Breakpoint.Delete(num)
        if debug > 0: print "debugger.Breakpoint.Delete(num) : Num =", num, ", Addr = 0x" + format(addr, "08x")
        del BrkCond[type][addr]
        if debug > 0: print "debugger.Breakpoint.Information()"
        if debug > 0: debugger.Breakpoint.Information()
    except:
        pass
    return "OK"

DebNotRun = True

def DebReset():
    global DebNotRun
    DebNotRun = True
    try:
        if debug > 0: print "debugger.Reset()"
        debugger.Reset()
    except:
        pass
    return

def DebGo():
    global DebReqStop
    try:
        if debug > 0: print "debugger.Go()"
        debugger.Go()
    except:
        # 失敗した時はSIGINTを送るようにしてみる
        DebWaitStop = True
        SendPacket(DebGetStatus())
    return

def DebStep():
    try:
        if debug > 0: print "debugger.Step()"
        debugger.Step()
    except:
        # 失敗した時はSIGINTを送るようにしてみる
        DebWaitStop = True
        SendPacket(DebGetStatus())
    return

def DebStop():
    try:
        if debug > 0: print "debugger.Stop()"
        debugger.Stop()
    except:
        pass
    return

DebWaitStop = False

def DebGetStatus():
    # Status : 'T' + <Sig[2桁]> + <RegId[2桁]> + ':' + <RegData[8桁(LBF)]> + ';' ...
    # Watchpointブレーク時 :    + <"watch"|"rwatch"|"awatch"> + ':' + <Addr[8桁(HBF)] + ';'
    global DebWaitStop
    print "Break Status"
    if DebNotRun == False:
        try:
            if debug > 0: print "debugger.GetBreakStatus()"
            brk = debugger.GetBreakStatus()
        except:
            brk = BreakStatus.None
            print brk
    else:
        brk = BreakStatus.None
        print brk
    if DebWaitStop == True:
        DebWaitStop = False
        sig = 2  # SIGINT
    elif brk == BreakStatus.None:
        sig = 5  # SIGTRAP 適切な割付ではないかもしれない
    elif brk == BreakStatus.Step:
        sig = 5  # SIGTRAP
    elif brk == BreakStatus.Manual:
        sig = 2  # SIGINT
    elif brk == BreakStatus.Event or brk == BreakStatus.Software or brk == BreakStatus.Temporary:
        sig = 5  # SIGTRAP
    elif brk == BreakStatus.TraceFull:
        sig = 5  # SIGTRAP 適切な割付ではないかもしれない
    elif brk == BreakStatus.NonMap or brk == BreakStatus.WriteProtect:
        sig = 11 # SIGSEGV 適切な割付ではないかもしれない
    elif brk == BreakStatus.IorIllegal or brk == BreakStatus.UninitializeMemoryRead:
        sig = 10 # SIGBUS 適切な割付ではないかもしれない
    else: # 有り得ないが念の為
        sig = 5  # SIGTRAP 適切な割付ではないかもしれない
    # TODO: PC以外にSP(R3),FP(R29),LP(R31)のレジスタ情報を返す
    # TODO: Watchpointブレークの情報を返したいがCubeSuite+固有のPythonオブジェクトでは不可能
    return "T" + format(sig, "02x") + "40:" + RegGetVal("pc") + ";"

#def DebAsyncCallbackBeforeCpuRun():
#    return

def DebAsyncCallbackAfterCpuStop():
    try:
        SendPacket(DebGetStatus())
    except:
        pass
    return

def MonExec(cmd):
    global debug, fixme, quit
    try:
        s = ""
        for i in range(0, len(cmd), 2):
            s += chr(int(cmd[i:i+2], 16))
    except:
        pass
    print "monitor", s
    try:
        t = s.strip().replace("\t", " ")
        u = t.replace(" ", "")
        v = ""
        if t.find("common.") == 0 or t.find("project.") == 0 or t.find("build.") == 0 or t.find("debugger.") == 0:
            v = eval(s)
        elif t == "reset":
            s = "debugger.Reset()"
            if debug > 0: print s
            v = eval(s)
        elif t.find("load ") == 0:
            s = "debugger.Download.Hex(\"" + s[s.find("load")+4:].strip() + "\")"
            if debug > 0: print s
            v = eval(s)
        elif u.find("debug=") == 0:
            debug = int(s[s.find("=")+1:])
        elif u.find("fixme=") == 0:
            fixme = int(s[s.find("=")+1:])
        elif u.find("quit=") == 0:
            quit = int(s[s.find("=")+1:])
        elif u.find("eval(") == 0:
            v = eval(s[s.find("("):])
        else:
            try:
                output = StringIO.StringIO()
                sys.stdout = output
                sys.stderr = output
                exec s
                v = output.getvalue()
                output.close()
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
        if v == None:
            s = ""
            if debug > 0: print "DEBUG:", "(No available return value)"
        else:
            s = str(v)
            if debug > 0: print "DEBUG:", s
    except Exception as e:
        s = str(e)
        if debug > 0: print "DEBUG:", s
    try:
        ret = ""
        for i in range(len(s)):
            ret += format(ord(s[i]), "02x")
        ret += "0a" # "\n"
    except:
        pass
    return ret

def gdbserver():
    global DebNotRun, DebWaitStop
    BrkClear()
    DebReset()
    while True:
        cmd = Recv()
        if not cmd: break
        ack,sep,cmd = cmd.partition("$")
        if sep == "$":
            # 将来binary downloading対応する時は見直す必要がある
            cmd,sep,sum = cmd.partition("#")
            if sep == "#":
                ack += sum[2:]
                sum = sum[0:2]
            cal = format(CalcChecksum(cmd), "02x")
            if cal == sum:
                SendAck("+")
            else:
                print "Checksum Error : Str =", cmd, ", Calc = ", cal, ", Recv = ", sum
                SendAck("-")
                cmd = ""
        err = ack.strip("+-\x03")
        if err != "":
            print "Protocol Error : Ack =", err
            SendAck("-")
            cmd = ""
        if ack.find("-") >= 0:
            SendLastPacketAgain()
        if ack.find("\x03") >= 0:
            # Stop : '\x03'(^C)
            DebWaitStop = True
            print "^C"
            DebStop()
        if debug > 0 and cmd != "": print "DEBUG: cmd =", cmd
        # コマンドのディスパッチ
        # 略記: LBF = Low byte first, HBF = High byte first
        if cmd[0:1] == "":
            continue
        elif cmd[0:1] == "k":
            # Kill : 'k'
            print "kill"
            break
        elif cmd[0:1] == "g":
            # Read All Registers : 'g'
            print "Register Value"
            SendPacket(RegGetValAll())
        elif cmd[0:1] == "P":
            # Write a Register : 'P' + <Id[2桁]> + '=' + <Data[8桁(LBF)]>
            r = RegName[HexStrToVal(cmd[1:3], "")]
            SendPacket(RegSetVal(r, cmd[4:12]))
        elif cmd[0:1] == "m":
            # Read Memory : 'm' + <Addr[可変桁(HBF)]> + ',' + <Len[可変桁(HBF)]>
            addr, i = HexStrToVal(cmd[1:], ",", True)
            leng, j = HexStrToVal(cmd[1+i+1:], "", True)
            print "Memory Value (" + format(addr, "08x") + "," + format(addr + leng - 1, "08x") + ")"
            SendPacket(MemGetVal(addr, leng))
        elif cmd[0:1] == "M":
            # Write Memory : 'M' + <Addr[可変桁(HBF)]> + ',' + <Leng[可変桁(HBF)]> + ':' + <Data[可変桁(LBF)]>
            addr, i = HexStrToVal(cmd[1:], ",", True)
            leng, j = HexStrToVal(cmd[1+i+1:], ":", True)
            # GDB側での受信(?) or CubeSuite+側での送信(?) が暫くの間固まるような症状が出る時がある
            SendPacket(MemSetVal(addr, leng, (cmd[1+i+1+j+1:])))
            # FIXME: 対症療法的に余分なAckを送信することにしてみる(明らかに具合が良くなる)
            if fixme > 0: Send("+")
        elif cmd[0:1] == "c":
            # Continue : 'c' または 'c' + <Addr[可変桁(HBF)]>
            if len(cmd) > 1:
                val = HexStrToVal(cmd[1:], "")
                RegSetValPC(val)
            print "continue"
            print "Breakpoint Information"
            if debug > 0: print "debugger.Breakpoint.Information()"
            debugger.Breakpoint.Information()
            DebNotRun = False
            # Continueの場合は実行中断待ちをクリアしておく
            DebWaitStop = False # clear
            DebGo()
        elif cmd[0:1] == "s":
            # Step : 's' または 's' + <Addr[可変桁(HBF)]>
            if len(cmd) > 1:
                val = HexStrToVal(cmd[1:], "")
                RegSetValPC(val)
            print "step"
            DebNotRun = False
            # Stepの場合は実行中断待ちを継続させておく
            DebWaitStop = DebWaitStop # keep
            DebStep()
        elif cmd[0:1] == "?":
            # Query Last Signal Code : '?'
            SendPacket(DebGetStatus())
        elif cmd[0:1] == "Z":
            # Set a Breakpoint : 'Z' + <N> + ','  + <Addr[可変桁(HBF)]> + ',' + <Len[可変桁(HBF)?]
            # N = '0' : Software Breakpoint
            # N = '1' : Hardware Breakpoint
            # N = '2' : Write Watchpoint
            # N = '3' : Read Watchpoint
            # N = '4' : Access Watchpoint
            addr = HexStrToVal(cmd[3:], ",")
            SendPacket(BrkSetBp(addr, cmd[1:2]))
        elif cmd[0:1] == "z":
            # Delete a Breakpoint : 'Z' + <N> + ','  + <Addr[可変桁(HBF)]> + ',' + <Len[可変桁(HBF)?]
            # N = '0' : Software Breakpoint
            # N = '1' : Hardware Breakpoint
            # N = '2' : Write Watchpoint
            # N = '3' : Read Watchpoint
            # N = '4' : Access Watchpoint
            addr = HexStrToVal(cmd[3:], ",")
            SendPacket(BrkDelBp(addr, cmd[1:2]))
        elif cmd[0:6] == "qRcmd,":
            # Monitor Command : "qRcmd," + <Cmd[[可変桁(16進化文字列)]>
            SendPacket(MonExec(cmd[6:]))
        else:
            SendPacket("")
    DebReset()
    return

def GdbServer():
    global ToolType, sock, conn
    try:
        try:
            print ""
            print "GDBSERVER STARTED on CubeSuite+'s Python Console"
            print ""
            print "Debug Tool Type"
            if debug > 0: print "debugger.DebugTool.GetType()"
            ToolType = debugger.DebugTool.GetType()
            print "Is Connected"
            if debug > 0: print "debugger.IsConnected()"
            result = debugger.IsConnected()
            if result == False:
                print "Now Connecting " + str(ToolType) + "..."
                if debug > 0: print "debugger.Connect()"
                debugger.Connect()
                print "Done"
                result = True
            print ""
        except:
            if debug > 0: print "DEBUG: exception @ debugger.DebugTool.GetType() ... debugger.Connect()"
            print ""
            raise
        sock = None
        conn = None
        retry = 0
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((HOST, PORT))
                sock.listen(1)
                print "WAITING for GDB..."
                # 以下の行でGDBの起動を待つ
                conn, addr = sock.accept()
                # GDBが起動した
                # 以下の2行で動的にスクリプト内の関数/変数の定義をアップデートする(/ps指定時は不可)
                common.Hook(SCRIPT)
                common.Source(SCRIPT)
                # 動的にスクリプト内の関数/変数の定義がアップデートされた(GdbServer()ブロック除く)
                print "GDB CONNECTED!"
                print ""
                if result == False:
                    if debug > 0: print "debugger.Connect()"
                    debugger.Connect()
                    result = True
                if debug > 0: print "DEBUG: Script is", SCRIPT
                if debug > 0: print "DEBUG: Script Version is", VERSION
                gdbserver()
                print ""
                print "GDB DISCONNECTED!"
                if quit == 1 or quit == 3:
                    if debug > 0: print "debugger.Disconnect()"
                    debugger.Disconnect()
                    result = False
                conn.close()
                conn = None
                sock.close()
                sock = None
                if quit >= 2:
                    break
            except:
                if debug > 0: print "DEBUG: exception @ sock = socket.socket() ... sock.close()"
                print ""
                try:
                    if conn != None:
                        conn.close()
                        conn = None
                    if sock != None:
                        sock.close()
                        sock = None
                except:
                    pass
                retry += 1
                if retry > MaxExceptRetry:
                    raise
        print "GDBSERVER TERMINATED by USER REQUEST"
        if quit == 2 or quit == 3:
            pass
        if quit == 4:
            if debug > 0: print "common.CubeSuiteExit()"
            common.CubeSuiteExit()
        print "Type GDBSERVER() to restart GDBSERVER on CubeSuite+'s Python Console"
        print ""
    except:
        print ""
        print "GDBSERVER TERMINATED by EXCEPTION"
        print ""

def GDBSERVER():
    global ScriptStarted
    try:
        ScriptStarted = True
        # 以下の2行で動的にスクリプト内の関数/変数の定義をアップデートする(/ps指定時は不可)
        common.Hook(SCRIPT)
        common.Source(SCRIPT)
        # 動的にスクリプト内の関数/変数の定義がアップデートされた(GdbServer()ブロック含む)
        GdbServer()
        ScriptStarted = False
    except:
        pass

################################
# フック関数とコールバック関数 #
################################

def BeforeDownload():
    return

def AfterDownload():
    return

def AfterCpuReset():
    return

def BeforeCpuRun():
#    DebAsyncCallbackBeforeCpuRun()
    return

def AfterCpuStop():
    DebAsyncCallbackAfterCpuStop()
    return

# 呼び出されない???
def pythonConsoleCallback(Id):
    if debug > 0: print "DEBUG: pythonConsoleCallback(" + Id + ")"
#    if Id == 20:
#        pass
#    elif Id == 12:
#        DebAsyncCallbackBeforeCpuRun()
#    elif Id == 13:
#        DebAsyncCallbackAfterCpuStop()
    return

############################
# スクリプトのトップレベル #
############################

try:
    # 変数が定義済みかどうかチェック(変数が定義されていなければ例外が発生する)
    if ScriptStarted == False:
        pass
except:
    ScriptStarted = False
try:
    # スクリプトが実行中かどうかチェック(スクリプトが再帰的に実行されるのを防止する)
    if ScriptStarted == False:
        ScriptStarted = True
        GdbServer()
        ScriptStarted = False
except:
    ScriptStarted = False
