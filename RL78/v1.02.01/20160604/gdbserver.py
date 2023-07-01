# GDBSERVER on CubeSuite+'s Python Console (for Renesas RL78 Simulator)
# coding=iso-2022-jp

# USAGE:
# �N�����@(�K�v�ɉ����ăp�X��t������K�v������܂�)
#   (1) CubeSuite+.exe /ps gdbserver.py �v���W�F�N�g�t�@�C����.mtpj
#       �I�������鎞��CTRL+Break�ŏI�������܂�(CubeSuite+.exe�̓R���\�[���A�v���P�[�V�����ł�)
#       CPU�g�p����100%�ɒ���t����肪����܂�
#       ���I�Ɏ������g�̃X�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g���邱�Ƃ��o���܂���
#   (2) CubeSuiteW+.exe /ps gdbserver.py �v���W�F�N�g�t�@�C����.mtpj
#       CPU�g�p����100%�ɒ���t����肪����܂�
#       ���I�Ɏ������g�̃X�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g���邱�Ƃ��o���܂���
#   (3) CubeSuiteW+.exe �v���W�F�N�g�t�@�C����.mtpj
#       �ȉ��̓��e�Ńv���W�F�N�g�t�@�C����.py�Ƃ����X�N���v�g�t�@�C�����쐬���Ă����܂�
#       common.Source("gdbserver.py")
#       �Ȃ��A���̓��e�Ƀp�X��t������ꍇ�A�ȉ���2�ʂ�̕\�L���@������܂�
#       (��)
#       common.Source(r"E:\tools\micom\Renesas\e2-P-Helios\workspace\Python\gdbserver.py")
#       common.Source("E:/tools/micom/Renesas/e2-P-Helios/workspace/Python\gdbserver.py")
#       CPU�g�p����100%�ɒ���t�����͂���܂���
#       ���I�Ɏ������g�̃X�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g���邱�Ƃ��o���܂�
# ���j�^�R�}���h
#   monitor python_statement
#     Python�̕������s���܂�
#   monitor exec "python_statement"
#     ����(HEW Target Server�łƎd�l�����킹�����Ēǉ����܂���)
#   monitor eval(python_expression)
#     Python�̎���]�����܂�
#   monitor reset
#     CubeSuite+�̃f�o�b�O�c�[�����CPU�����Z�b�g���܂�
#   monitor load �t�@�C����.hex
#     CubeSuite+�̃f�o�b�O�c�[�����HEX�t�@�C�����_�E�����[�h���܂�
#     CubeSuite+��HEX�t�@�C���ƔF��������̂ł���΃t�@�C���̊g���q�͉��ł��\���܂���
#   monitor load xcoff78k �t�@�C����.lmf
#     CubeSuite+�̃f�o�b�O�c�[�����XCOFF78K�t�@�C�����_�E�����[�h���܂�
#     CubeSuite+��XCOFF78K�t�@�C���ƔF��������̂ł���΃t�@�C���̊g���q�͉��ł��\���܂���
#   monitor debug = 0(�f�t�H���g)/1
#     debug = 0 : Python�R���\�[����Ƀf�o�b�O���b�Z�[�W��\�����܂���
#     debug = 1 : Python�R���\�[����Ƀf�o�b�O���b�Z�[�W��\�����܂�
#   monitor fixme = 0/1(�f�t�H���g)
#     fixme = 0 : �s��̑ΏǗÖ@�I�ȑΏ��𖳌��ɂ��܂�
#     fixme = 1 : �s��̑ΏǗÖ@�I�ȑΏ���L���ɂ��܂�
#   monitor quit = 0(�f�t�H���g)/1/2/3/4
#     quit = 0 : GDB�I������GDBSERVER�X�N���v�g���I�����܂���(�f�o�b�O�c�[�����ؒf���܂���)
#     quit = 1 : GDB�I������GDBSERVER�X�N���v�g���I�����܂���(�f�o�b�O�c�[���͐ؒf���܂�)
#     quit = 2 : GDB�I������GDBSERVER�X�N���v�g���I�����܂�(�f�o�b�O�c�[���͐ؒf���܂���)
#     quit = 3 : GDB�I������GDBSERVER�X�N���v�g���I�����܂�(�f�o�b�O�c�[�����ؒf���܂�)
#     quit = 4 : GDB�I������CubeSuite+���I�����܂�
# 
# FIXME:
# ���������C�g���^�C���A�E�g���邱�Ƃ��������B�ΏǗÖ@�I�ɑΏ��������A�K�؂ȕ��@��???
# �X�e�b�v���s�𒆒f��������GDB���G���[��\�����邱�Ƃ��������B^C�̗L���̐�ǂ݂��K�v��???
# ��L��������A���o�[�W������CubeSuite+�ŋN���Ă����Ǐ�ł��邪�A�ŐV�o�[�W������CubeSuite+��
# �Ǐ󂪍Č����邩�ǂ����m�F�o���Ă��Ȃ��B�ȒP�ɏǏ󂪏o��Ƃ������R�ōČ�����ۑ����Y�ꂽ�B
#
# TODO:
# �u���[�N����Watchpoint�u���[�N�̏���Ԃ�������CubeSuite+�ŗL��Python�I�u�W�F�N�g�ł͕s�\
# �K�؂ȃG���[��GDB�֕Ԃ�������GDB�̃G���[�R�[�h�𒲂ׂȂ��ƕԂ��Ȃ�
# ���������[�h���C�g�̌�����(���1�o�C�g�Â�����������͌������ǂ��Ȃ�)
# CubeSuite+�̋N���I�v�V����/ps�ŃX�N���v�g���w�肷���CPU�g�p����100���ɒ���t�����̉��
# �����Ԏg�p���̓���̈��萫�͂ǂ����낤��?
#
# MEMO:
# CubeSuiteW+.exe �v���W�F�N�g�t�@�C����.mtpj �̏ꍇ�� �v���W�F�N�g�t�@�C����.py �����s�����
# CubeSuite+.exe �v���W�F�N�g�t�@�C����.mtpj �̏ꍇ�� �v���W�F�N�g�t�@�C����.py �����s����Ȃ�

import socket, time, StringIO

HOST = "localhost"
PORT = 2159

debug = 0
fixme = 1 # �Ƃ肠����
quit = 0

MODULE = str(sys.modules["__main__"])
SCRIPT = MODULE[MODULE.find(" from ")+7:-2]
VERSION = "v1.02.01.00" # 2016/06/04
SVNAME = "CS+'s Python Console"

MaxRecvPacket = 4096
MaxExceptRetry = 100
SockTimeOut = 10.0
LastPacketData = ""

def Recv():
    global conn
    while True:
        try:
            data = conn.recv(MaxRecvPacket)
        except socket.timeout:
            continue
        except:
            if debug > 0: print "DEBUG: exception @ data = conn.recv()"
            raise
        else:
            break
    if debug > 0: print "RECV:", repr(data)
    return data

def Send(data):
    global conn
    while True:
        try:
            conn.sendall(data)
        except socket.timeout:
            continue
        except:
            if debug > 0: print "DEBUG: exception @ conn.send()"
            raise
        else:
            break
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

# Note: High byte first
def ValToHexData_BigEndian(val, col = 8):
    hex = ""
    for i in range(0, col, 2):
        hex = format((val / (1 << (4 * i))) % 256, "02x") + hex
    return hex

# Note: High byte first
def HexDataToVal_BigEndian(hex):
    val = 0
    for i in range(0, len(hex), 2):
        try:
            val = (val << 8) + int(hex[i:i+2], 16)
        except:
            pass
    return val

RegEndian = "L" # "B"(for BigEndian) or "L"(for LittleEndian)
# �i��ɂ���Ă�mem���W�X�^�����݂��Ȃ��ꍇ������
RegName = [\
    "x:rb0", "a:rb0", "c:rb0", "b:rb0", "e:rb0", "d:rb0", "l:rb0", "h:rb0", \
    "x:rb1", "a:rb1", "c:rb1", "b:rb1", "e:rb1", "d:rb1", "l:rb1", "h:rb1", \
    "x:rb2", "a:rb2", "c:rb2", "b:rb2", "e:rb2", "d:rb2", "l:rb2", "h:rb2", \
    "x:rb3", "a:rb3", "c:rb3", "b:rb3", "e:rb3", "d:rb3", "l:rb3", "h:rb3", \
    "psw", "es", "cs", "pc", "sp_l", "sp_h", "pmc", "mem"]
RegCol  = [\
    2, 2, 2, 2, 2, 2, 2, 2, \
    2, 2, 2, 2, 2, 2, 2, 2, \
    2, 2, 2, 2, 2, 2, 2, 2, \
    2, 2, 2, 2, 2, 2, 2, 2, \
    2, 2, 2, 8, 2, 2, 2, 2]
RegAll = range(0, 0x28)
RegAtBrk = range(0x23,0x26) # pc, sp_l, sp_h
RegExcl = ""

def RegGetVal_(reg):
    global RegExcl
    val = 0
    try:
        if reg == "":
            return 0
        elif reg == "mem" and RegExcl.find("mem:") != -1:
            return 0
        elif reg == "sp_l":
            mask = 0x00ff
            shft = 0
            reg = "sp"
        elif reg == "sp_h":
            mask = 0xff00
            shft = 8
            reg = "sp"
        else:
            mask = 0xffffffff
            shft = 0
        if debug > 0: print "debugger.Register.GetValue() : Reg =", reg, ", Val = "
        val = (int(debugger.Register.GetValue(reg)) & mask) >> shft
        if debug > 0: print "0x" + format(val, "08x")
    except:
        if reg == "mem":
            if debug > 0: print "(No more access to 'mem' register)"
            RegExcl += "mem:"
        pass
    return val

def RegSetVal_(reg, val):
    global RegExcl
    try:
        if reg == "":
            return
        elif reg == "mem" and RegExcl.find("mem:") != -1:
            return
        elif reg == "sp_l":
            reg = "sp"
            if debug > 0: print "debugger.Register.GetValue() : Reg =", reg, ", Val = "
            tmp = int(debugger.Register.GetValue(reg), 16)
            val = ((val << 0) & 0x00ff) | (tmp & 0xff00)
        elif reg == "sp_h":
            reg = "sp"
            if debug > 0: print "debugger.Register.GetValue() : Reg =", reg, ", Val = "
            tmp = int(debugger.Register.GetValue(reg), 16)
            val = ((val << 8) & 0xff00) | (tmp & 0x00ff)
        if debug > 0: print "debugger.Register.SetValue() : Reg =", reg, ", Val = 0x" + format(val, "08x")
        debugger.Register.SetValue(reg, val)
    except:
        pass
    return

# Note: Low byte first or High byte first
def RegGetVal(id):
    col = 2
    val = 0
    try:
        col = RegCol[id]
        val = RegGetVal_(RegName[id])
    except:
        pass
    if RegEndian == "L":
        return ValToHexData(val, col)
    else:
        return ValToHexData_BigEndian(val, col)

# Note: Low byte first or High byte first
def RegSetVal(id, val):
    try:
        if RegEndian == "L":
            RegSetVal_(RegName[id], HexDataToVal(val))
        else:
            RegSetVal_(RegName[id], HexDataToVal_BigEndian(val))
    except:
        pass
    return "OK"

def RegGetValAll():
    ret = ""
    for id in RegAll:
        ret += RegGetVal(id)
    return ret

def RegSetValPC(val):
    RegSetVal_("pc", val)
    return

# TODO: �G���[�������͂ǂ�����?
# TODO: ������(���1�o�C�g�Â�����������͌������ǂ��Ȃ�)
# Note: Low byte first
def MemGetVal(addr, leng):
    if debug > 0: print "debugger.Memory.Read() : Addr = 0x" + format(addr, "08x"), ", Len = 0x" + format(leng, "08x")
    ret = ""
    # addr, addr + leng�̒l�̃^���p�v���[�t�͕K�v?
    for a in range(addr, addr + leng):
        val = 0
        try:
            val = int(debugger.Memory.Read(a, MemoryOption.Byte))
            if debug > 0: print format(val, "02x")
        except:
            pass
        ret += format(val, "02x")
    return ret

# TODO: �G���[�������͂ǂ�����?
# TODO: ������(���1�o�C�g�Â�����������͌������ǂ��Ȃ�)
# Note: Low byte first
def MemSetVal(addr, leng, data):
    if debug > 0: print "debugger.Memory.Write() : Addr = 0x" + format(addr, "08x"), ", Len = 0x" + format(leng, "08x")
    # addr, addr + leng�̒l�̃^���p�v���[�t�͕K�v?
    for i in range(0, len(data), 2):
        try:
            debugger.Memory.Write(addr, int(data[i:i+2], 16), MemoryOption.Byte)
        except:
            pass
        addr += 1
    return "OK"

# �u���[�N�|�C���g�̊Ǘ��Ƀf�B�N�V���i��(�A�z�z��)���g���Ă݂�
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
    try:
        if debug > 0: print "debugger.Breakpoint.Delete()"
        debugger.Breakpoint.Delete()
        BrkCond[BreakType.Software] = {}
        BrkCond[BreakType.Hardware] = {}
        BrkCond[BreakType.Write] = {}
        BrkCond[BreakType.Read] = {}
        BrkCond[BreakType.Access] = {}
    except:
        pass
    return

def BrkInfo():
    if debug > 0: print "debugger.Breakpoint.Information()"
    debugger.Breakpoint.Information()
    print common.Output
    return

# TODO: �G���[�������͂ǂ�����?
def BrkSetBp(addr, type):
    global ToolType, BrkType, BrkCond
    try:
        type = BrkType[type]
        if type == BreakType.Software and ToolType == DebugTool.Simulator:
            type = BreakType.Hardware
        num = debugger.Breakpoint.Set(BreakCondition(Address = addr, BreakType = type))
        if debug > 0: print "debugger.Breakpoint.Set(cond) : Num =", num, ", Addr = 0x" + format(addr, "08x")
        BrkCond[type][addr] = num
        if debug > 0: BrkInfo()
    except:
        pass
    return "OK"

# TODO: �G���[�������͂ǂ�����?
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
        if debug > 0: BrkInfo()
    except:
        pass
    return "OK"

DebNotRun = True
DebWaitStop = False

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
    global DebNotRun, DebWaitStop
    if debug > 0: BrkInfo()
    DebNotRun = False
    # Continue�̏ꍇ�͎��s���f�҂����N���A���Ă���
    DebWaitStop = False # clear
    try:
        if debug > 0: print "debugger.Go()"
        debugger.Go()
    except:
        # ���s��������SIGINT�𑗂�悤�ɂ��Ă݂�
        DebWaitStop = True
        SendPacket(DebGetStatus())
    return

def DebStep():
    global DebNotRun, DebWaitStop
    DebNotRun = False
    # Step�̏ꍇ�͎��s���f�҂����p�������Ă���
    DebWaitStop = DebWaitStop # keep
    try:
#        if debug > 0: print "debugger.Step(StepOption.Source)"
#        debugger.Step(StepOption.Source)
        if debug > 0: print "debugger.Step(StepOption.Instruction)"
        debugger.Step(StepOption.Instruction)
    except:
        # ���s��������SIGINT�𑗂�悤�ɂ��Ă݂�
        DebWaitStop = True
        SendPacket(DebGetStatus())
    return

def DebStop():
    global DebWaitStop
    DebWaitStop = True
    try:
        if debug > 0: print "debugger.Stop()"
        debugger.Stop()
    except:
        pass
    return

def DebGetStatus():
    # Status : 'T' + <Sig[2��]> + <RegId[2��]> + ':' + <RegData[2,8��(LBF)]> + ';' ...
    # Watchpoint�u���[�N�� :    + <"watch"|"rwatch"|"awatch"> + ':' + <Addr[8��(HBF)] + ';'
    global DebNotRun, DebWaitStop
    if debug > 0: print "Break Status"
    brk = BreakStatus.None
    if DebNotRun == False and DebWaitStop == False:
        try:
            if debug > 0: print "debugger.GetBreakStatus()"
            brk = debugger.GetBreakStatus()
            if debug > 0: print brk
        except:
            pass
    if DebNotRun == True:
        if debug > 0: print "Go/Step is not performed"
    if DebWaitStop == True:
        if debug > 0: print "Manually Stop is requested"
    if DebWaitStop == True:
        DebWaitStop = False
        sig = 2  # SIGINT
    elif brk == BreakStatus.None:
        sig = 5  # SIGTRAP �K�؂Ȋ��t�ł͂Ȃ���������Ȃ�
    elif brk == BreakStatus.Step:
        sig = 5  # SIGTRAP
    elif brk == BreakStatus.Manual:
        sig = 2  # SIGINT
    elif brk == BreakStatus.Event or brk == BreakStatus.Software or brk == BreakStatus.Temporary:
        sig = 5  # SIGTRAP
    elif brk == BreakStatus.TraceFull:
        sig = 5  # SIGTRAP �K�؂Ȋ��t�ł͂Ȃ���������Ȃ�
    elif brk == BreakStatus.NonMap or brk == BreakStatus.WriteProtect:
        sig = 11 # SIGSEGV �K�؂Ȋ��t�ł͂Ȃ���������Ȃ�
    elif brk == BreakStatus.IorIllegal or brk == BreakStatus.UninitializeMemoryRead:
        sig = 10 # SIGBUS �K�؂Ȋ��t�ł͂Ȃ���������Ȃ�
    else: # �L�蓾�Ȃ����O�̈�
        sig = 5  # SIGTRAP �K�؂Ȋ��t�ł͂Ȃ���������Ȃ�
    if debug > 0: print "Signal = ", sig
    # TODO: Watchpoint�u���[�N�̏���Ԃ�������CubeSuite+�ŗL��Python�I�u�W�F�N�g�ł͕s�\
    ret = "T" + format(sig, "02x")
    for id in RegAtBrk:
        ret += format(id, "02x") + ":" + RegGetVal(id) + ";"
    return ret

#def DebAsyncCallbackBeforeCpuRun():
#    return

def DebAsyncCallbackAfterCpuStop():
    if DebNotRun == True:
        return
    try:
        SendPacket(DebGetStatus())
        # GDB���ł̎�M(?) or CubeSuite+���ł̑��M(?) ���b���̊Ԍł܂�悤�ȏǏ󂪏o�鎞������
        # FIXME: �ΏǗÖ@�I�ɗ]����Ack�𑗐M���邱�Ƃɂ��Ă݂�(���o�[�W������CubeSuite+�Ŗ��炩��
        # ����ǂ��Ȃ������Ƃ��������B�ŐV�o�[�W������CubeSuite+�ŏǏ󂪍Č����邩�ǂ����m�F
        # �o���Ă��Ȃ��B�ȒP�ɏǏ󂪏o��Ƃ������R�ōČ�����ۑ����Y��Ă��܂������Ԃł���B)
        if fixme > 0: Send("+")
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
    if debug > 0: print "monitor", s
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
        elif t.find("load xcoff78k ") == 0:
            s = "debugger.Download.LoadModule(\"" + s[s.find("load xcoff78k")+13:].strip() + "\")"
            if debug > 0: print s
            v = eval(s)
        elif t.find("load Elf/Dwarf2 ") == 0:
            s = "debugger.Download.LoadModule(\"" + s[s.find("load Elf/Dwarf2")+15:].strip() + "\")"
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
        elif u.find("exec\"") == 0:
            try:
                output = StringIO.StringIO()
                sys.stdout = output
                sys.stderr = output
                exec s[s.find("\"")+1:].strip("\"")
                v = output.getvalue()
                output.close()
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
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
    BrkClear()
#    # CubeSuite+�����ł܂�Ǐ󂪏o��̂łƂ肠�����R�����g�A�E�g����
#    DebReset()
    while True:
        cmd = Recv()
        if not cmd: break
        ack,sep,cmd = cmd.partition("$")
        if sep == "$":
            # ����binary downloading�Ή����鎞�͌������K�v������
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
            if debug > 0: print "^C"
            DebStop()
        if debug > 0 and cmd != "": print "DEBUG: cmd =", cmd
        # �R�}���h�̃f�B�X�p�b�`
        # ���L: LBF = Low byte first, HBF = High byte first
        if cmd[0:1] == "":
            continue
        elif cmd[0:1] == "k":
            # Kill : 'k'
            if debug > 0: print "kill"
            break
        elif cmd[0:1] == "g":
            # Read All Registers : 'g'
            # RL78�ł̓��W�X�^�l��GDB�֑���Ԃ����̌X��Data�̃o�C�g�I�[�_�[��LBF
            SendPacket(RegGetValAll())
#        # �����Ă��������̂ŃR�����g�A�E�g���Ă���(�f�o�b�O�ɕ֗��������̂ŃR�[�h�͎c���Ă���)
#        elif cmd[0:1] == "p":
#            # Read a Register : 'p' + <Id[1,2��]>
#            # RL78�ł̓��W�X�^�l��GDB�֑���Ԃ����̌X��Data�̃o�C�g�I�[�_�[��LBF
#            id, i = HexStrToVal(cmd[1:], "", True)
#            SendPacket(RegGetVal(id))
        elif cmd[0:1] == "P":
            # Write a Register : 'P' + <Id[1,2��]> + '=' + <Data[�ό�(RL78�ł̓o�C�g�I�[�_�[��LBF)]>
            id, i = HexStrToVal(cmd[1:], "=", True)
            SendPacket(RegSetVal(id, cmd[1+i+1:]))
        elif cmd[0:1] == "m":
            # Read Memory : 'm' + <Addr[�ό�(HBF)]> + ',' + <Len[�ό�(HBF)]>
            # ���������e��GDB�֑���Ԃ�����Data�̃o�C�g�I�[�_�[��LBF
            addr, i = HexStrToVal(cmd[1:], ",", True)
            leng, j = HexStrToVal(cmd[1+i+1:], "", True)
            SendPacket(MemGetVal(addr, leng))
        elif cmd[0:1] == "M":
            # Write Memory : 'M' + <Addr[�ό�(HBF)]> + ',' + <Len[�ό�(HBF)]> + ':' + <Data[�ό�(LBF)]>
            addr, i = HexStrToVal(cmd[1:], ",", True)
            leng, j = HexStrToVal(cmd[1+i+1:], ":", True)
            # GDB���ł̎�M(?) or CubeSuite+���ł̑��M(?) ���b���̊Ԍł܂�悤�ȏǏ󂪏o�鎞������
            SendPacket(MemSetVal(addr, leng, (cmd[1+i+1+j+1:])))
            # FIXME: �ΏǗÖ@�I�ɗ]����Ack�𑗐M���邱�Ƃɂ��Ă݂�(���o�[�W������CubeSuite+�Ŗ��炩��
            # ����ǂ��Ȃ������Ƃ��������B�ŐV�o�[�W������CubeSuite+�ŏǏ󂪍Č����邩�ǂ����m�F
            # �o���Ă��Ȃ��B�ȒP�ɏǏ󂪏o��Ƃ������R�ōČ�����ۑ����Y��Ă��܂������Ԃł���B)
            if fixme > 0: Send("+")
        elif cmd[0:1] == "c":
            # Continue : 'c' �܂��� 'c' + <Addr[�ό�(HBF)]>
            if len(cmd) > 1:
                val = HexStrToVal(cmd[1:], "")
                RegSetValPC(val)
            if debug > 0: print "continue"
            DebGo()
        elif cmd[0:1] == "s":
            # Step : 's' �܂��� 's' + <Addr[�ό�(HBF)]>
            if len(cmd) > 1:
                val = HexStrToVal(cmd[1:], "")
                RegSetValPC(val)
            if debug > 0: print "step"
            DebStep()
        elif cmd[0:1] == "?":
            # Query Last Signal Code : '?'
            SendPacket(DebGetStatus())
        elif cmd[0:1] == "Z":
            # Set a Breakpoint : 'Z' + <N> + ','  + <Addr[�ό�(HBF)]> + ',' + <Len[�ό�(HBF)?]
            # N = '0' : Software Breakpoint
            # N = '1' : Hardware Breakpoint
            # N = '2' : Write Watchpoint
            # N = '3' : Read Watchpoint
            # N = '4' : Access Watchpoint
            addr = HexStrToVal(cmd[3:], ",")
            SendPacket(BrkSetBp(addr, cmd[1:2]))
        elif cmd[0:1] == "z":
            # Delete a Breakpoint : 'Z' + <N> + ','  + <Addr[�ό�(HBF)]> + ',' + <Len[�ό�(HBF)?]
            # N = '0' : Software Breakpoint
            # N = '1' : Hardware Breakpoint
            # N = '2' : Write Watchpoint
            # N = '3' : Read Watchpoint
            # N = '4' : Access Watchpoint
            addr = HexStrToVal(cmd[3:], ",")
            SendPacket(BrkDelBp(addr, cmd[1:2]))
        elif cmd[0:6] == "qRcmd,":
            # Monitor Command : "qRcmd," + <Cmd[[�ό�(16�i��������)]>
            SendPacket(MonExec(cmd[6:]))
        else:
            SendPacket("")
    DebReset()
    return

def GdbServer():
    global ToolType, sock, conn
    try:
        if debug > 0: print ""
        if debug > 0: print "GDBSERVER STARTED on " + SVNAME
        common.OutputPanel("GDBSERVER STARTED on " + SVNAME)
        try:
            if debug > 0: print ""
            if debug > 0: print "debugger.DebugTool.GetType()"
            ToolType = debugger.DebugTool.GetType()
            if debug > 0: print ToolType
            if debug > 0: print ""
            if debug > 0: print "debugger.IsConnected()"
            result = debugger.IsConnected()
            if debug > 0: print result
        except:
            if debug > 0: print "DEBUG: exception @ debugger.DebugTool.GetType() ... debugger.Connect()"
            print ""
            raise
        sock = None
        conn = None
        retry = 0
        while True:
            try:
                if sock == None:
                    if debug > 0: print "socket opening..."
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind((HOST, PORT))
                    sock.listen(1)
                    sock.settimeout(SockTimeOut)
                    if debug > 0: print "socket opened"
                if debug > 0: print ""
                if debug > 0: print "WAITING for GDB..."
                common.OutputPanel("WAITING for GDB...")
                # �ȉ���GDB�̋N����҂�
                while True:
                    try:
                        conn, addr = sock.accept()
                    except socket.timeout:
                        continue
                    except:
                        raise
                    else:
                        break
                # GDB���N������
                # �ȉ���2�s�œ��I�ɃX�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g����(/ps�w�莞�͕s��)
                common.Hook(SCRIPT)
                common.Source(SCRIPT)
                # ���I�ɃX�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g���ꂽ(GdbServer()�u���b�N����)
                if debug > 0: print ""
                if debug > 0: print "GDB CONNECTED!"
                if debug > 0: print ""
                common.OutputPanel("GDB CONNECTED!")
                if debug > 0: print "debugger.IsConnected()"
                result = debugger.IsConnected()
                if debug > 0: print result
                if debug > 0: print ""
                if result == False:
                    if debug > 0: print "debugger.Connect()"
                    if debug > 0: print ""
                    debugger.Connect()
                    result = True
                if debug > 0: print "DEBUG: Script is", SCRIPT
                if debug > 0: print "DEBUG: Script Version is", VERSION
                if debug > 0: print ""
                gdbserver()
                if debug > 0: print ""
                if debug > 0: print "GDB DISCONNECTED!"
                if debug > 0: print ""
                common.OutputPanel("GDB DISCONNECTED!")
                if quit == 1 or quit == 3:
                    if debug > 0: print "debugger.Disconnect()"
                    if debug > 0: print ""
                    debugger.Disconnect()
                    result = False
                conn.close()
                conn = None
                if quit >= 2:
                    break
            except:
                if debug > 0: print "DEBUG: exception @ sock = socket.socket() ... conn.close()"
                print ""
                try:
                    if conn != None:
                        conn.close()
                        conn = None
                except:
                    pass
                retry += 1
                if retry > MaxExceptRetry:
                    raise
                time.sleep(1.0)
        if sock != None:
            sock.close()
            sock = None
        if debug > 0: print "GDBSERVER TERMINATED by USER REQUEST"
        if quit == 2 or quit == 3:
            pass
        if quit == 4:
            if debug > 0: print "common.CubeSuiteExit()"
            common.CubeSuiteExit()
        if debug > 0: print "Type GDBSERVER() to restart GDBSERVER on CubeSuite+'s Python Console"
        if debug > 0: print ""
    except:
        if debug > 0: print ""
        if debug > 0: print "GDBSERVER TERMINATED by EXCEPTION"
        if debug > 0: print ""

def GDBSERVER():
    global ScriptStarted
    try:
        ScriptStarted = True
        # �ȉ���2�s�œ��I�ɃX�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g����(/ps�w�莞�͕s��)
        common.Hook(SCRIPT)
        common.Source(SCRIPT)
        # ���I�ɃX�N���v�g���̊֐�/�ϐ��̒�`���A�b�v�f�[�g���ꂽ(GdbServer()�u���b�N�܂�)
        GdbServer()
        ScriptStarted = False
    except:
        pass

################################
# �t�b�N�֐��ƃR�[���o�b�N�֐� #
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

def pythonConsoleCallback(Id):
#    if debug > 0: print "DEBUG: pythonConsoleCallback(" + str(Id) + ")"
#    if Id == 20:
#        pass
##    elif Id == 12:
##        DebAsyncCallbackBeforeCpuRun()
#    elif Id == 13:
#        DebAsyncCallbackAfterCpuStop()
    return

############################
# �X�N���v�g�̃g�b�v���x�� #
############################

try:
    # �ϐ�����`�ς݂��ǂ����`�F�b�N(�ϐ�����`����Ă��Ȃ���Η�O����������)
    if ScriptStarted == False:
        pass
except:
    ScriptStarted = False
try:
    # �X�N���v�g�����s�����ǂ����`�F�b�N(�X�N���v�g���ċA�I�Ɏ��s�����̂�h�~����)
    if ScriptStarted == False:
        UseRemoting = common.UseRemoting
        common.UseRemoting = False
        ThrowExcept = common.ThrowExcept
        common.ThrowExcept = True
        ViewOutput = common.ViewOutput
        common.ViewOutput = False
        ScriptStarted = True
        GdbServer()
        ScriptStarted = False
        common.UseRemoting = UseRemoting
        common.ThrowExcept = ThrowExcept
        common.ViewOutput = ViewOutput
except:
    ScriptStarted = False
    common.UseRemoting = UseRemoting
    common.ThrowExcept = ThrowExcept
    common.ViewOutput = ViewOutput
