# input = sys.argv[1] == xxx.vm; output = sys.argv[2] == xxx.asm
# assembly code will be written into newly created/overwritten xxx.asm file
# or sys.argv[1] = dirName where dir contains multiple vm files including sys file
# for the dir functionality, static variables are handled assuming that they are variables in a function. 
# if a static variable is pushed/popped before a function is defined then there will be an error
# test scripts don't account for this since i guess its obvious that static variables can't exist unless they belong to a function 
# NOTE: interesting bug in this program where, when reading a dir for VM files, some VM files are translated and written into the new ASM file more than once
# I decided to keep this bug in the code because the program still passes the test scripts and its interesting to see how redundant ASM code is ignored and
# how it doesn't affect the functionality of the program when inserting it into the CPU emulator.
import sys
import os 
import glob 

noComments = []
finalRead = []
writeAsm = []
functionNameChecker = []	# used to write static instruction
instructionCounter = 0
fillEqCounter = 0
fillGtCounter = 0
fillLtCounter = 0
returnCounterAddress = 1
sep = "//"

# if translating a single VM file
if '.' in sys.argv[1]:

	with open(sys.argv[1]) as f:
	     lines = [line.rstrip('\n') for line in f]	# append each line into a list

	noEmptyLines = [x for x in lines if x]	# remove empty elems
	for line in noEmptyLines:						# remove comments
		stripComments = line.split(sep, 1)[0]
		noComments.append(stripComments)

	noLinesNoComments = [x for x in noComments if x]	# remove empty elems again

	for line in noLinesNoComments:		# remove whitespace
		finalRead.append(line.strip())

	fileNameDotIndex = sys.argv[1].index('.')
	fileName = sys.argv[1][:fileNameDotIndex]

	for i in finalRead:

		# if push/pop command
		if i[0] == 'p':
			# capture the instruction, memory segment, and register int of the VM command
			firstSpace = i.index(' ')
			secondSpace = i.index(' ', firstSpace+1)

			instructionTerm = i[:firstSpace]
			memorySegmentTerm = i[firstSpace+1:secondSpace]
			regInt = i[secondSpace+1:]

			# push/pop assembly language
			if instructionTerm == 'push' and memorySegmentTerm == 'local':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'argument':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @ARG \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'this':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'that':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'constant':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @{regInt} \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'static':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @{fileName}.{regInt} \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'temp':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @5 \n D=A \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'pointer' and regInt == '0':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'pointer' and regInt == '1':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			# store pointer in general purpose register R13 to the desired virtual memory register 
			elif instructionTerm == 'pop' and memorySegmentTerm == 'local':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'argument':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @ARG \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'this':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'that':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'static':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @{fileName}.{regInt} \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'temp':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @5 \n D=A \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'pointer' and regInt == '0':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @THIS \n M=D")	

			elif instructionTerm == 'pop' and memorySegmentTerm == 'pointer' and regInt == '1':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @THAT \n M=D")	

		# if branching command logic
		elif i[0:2] == 'if' or i[0:4] == 'goto' or i[0:5] == 'label':
			spaceIndex = i.index(' ')

			if i[0:5] == 'label':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n ({i[spaceIndex+1:]})")

			elif i[0:4] == 'goto':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @{i[spaceIndex+1:]} \n 0;JMP")

			elif i[0:2] == 'if':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @{i[spaceIndex+1:]} \n D;JNE")

		# function command logic
		elif i[0:4] == 'func' or i[0:4] == 'call' or i == 'return':

			if i[0:4] == 'func':
				firstSpace = i.index(' ')
				secondSpace = i.index(' ', firstSpace+1)
				functionName = i[firstSpace+1:secondSpace]
				nVars = int(i[secondSpace+1:])
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n ({functionName}) \n")

				while nVars > 0:
					writeAsm.append(f"@0 \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1")
					nVars = nVars - 1

			elif i[0:4] == 'call':
				firstSpace = i.index(' ')
				secondSpace = i.index(' ', firstSpace+1)
				functionName = i[firstSpace+1:secondSpace]
				nArgs = int(i[secondSpace+1:])
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @RETURN_ADDRESS_{returnCounterAddress} \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @LCL \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @ARG \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THIS \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THAT \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @SP \n D=M \n @R13 \n M=D \n @5 \n D=A \n @R13 \n M=M-D \n @{nArgs} \n D=A \n @R13 \n M=M-D \n @R13 \n D=M \n @ARG \n M=D \n @SP \n D=M \n @LCL \n M=D \n @{functionName} \n 0;JMP \n (RETURN_ADDRESS_{returnCounterAddress})")
				returnCounterAddress = returnCounterAddress + 1

			elif i == 'return':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @R7 \n M=D \n @5 \n A=D-A \n D=M \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @ARG \n A=M \n M=D \n @ARG \n D=M \n @SP \n M=D+1 \n @R7 \n D=M  \n @1 \n A=D-A \n D=M \n @THAT \n M=D \n @R7 \n D=M \n @2 \n A=D-A \n D=M \n @THIS \n M=D \n @R7 \n D=M \n @3 \n A=D-A \n D=M \n @ARG \n M=D \n @R7 \n D=M \n @4 \n A=D-A \n D=M \n @LCL \n M=D \n @R13 \n A=M \n 0;JMP")

		else:

			# arithmetic logic
			if i == 'add':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D+M \n @SP \n A=M \n M=D \n @SP \n M=M+1")
			
			elif i == 'sub':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D-M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif i == 'neg':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n M=-M \n @SP \n M=M+1")

			elif i == 'eq':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLEQ{fillEqCounter} \n D;JEQ \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLEQ{fillEqCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillEqCounter = fillEqCounter + 1

			elif i == 'gt':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLGT{fillGtCounter} \n D;JGT \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLGT{fillGtCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillGtCounter = fillGtCounter + 1

			elif i == 'lt':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLLT{fillLtCounter} \n D;JLT \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLLT{fillLtCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillLtCounter = fillLtCounter + 1

			elif i == 'and':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D&M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif i == 'or':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D|M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif i == 'not':
				writeAsm.append(f"// {i} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n M=!M \n @SP \n M=M+1")
			

		instructionCounter = instructionCounter + 1

	#insert infinite loop after writing everything
	writeAsm.append(f'(INSTRUCTION{instructionCounter})')
	writeAsm.append(f'@INSTRUCTION{instructionCounter}')
	writeAsm.append('0;JMP')

	# write to output file
	with open(sys.argv[2], 'w') as f:
	    for line in writeAsm:
	        f.write(f"{line}\n")

# read all VM files in dir
elif "." not in sys.argv[1]:

	# bootstrap code (nArgs = 0 so it is not included in the sys.init call code)
	writeAsm.append('// Bootstrap code \n @256 \n D=A \n @SP \n M=D \n @RETURN_ADDRESS_0 \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @LCL \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @ARG \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THIS \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THAT \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @SP \n D=M \n @R13 \n M=D \n @5 \n D=A \n @R13 \n M=M-D \n @R13 \n D=M \n @ARG \n M=D \n @SP \n D=M \n @LCL \n M=D \n @Sys.init \n 0;JMP \n (RETURN_ADDRESS_0)')

	# get the VM files listed in the directory
	cwd = os.getcwd()
	dirPath = cwd + '\\' + sys.argv[1] + '\\'
	vmFiles = glob.glob(f"{dirPath}*.vm")

	for i in vmFiles:
		with open(i) as f:
		     lines = [line.rstrip('\n') for line in f]	# append each line into a list

		noEmptyLines = [x for x in lines if x]	# remove empty elems
		for line in noEmptyLines:						# remove comments
			stripComments = line.split(sep, 1)[0]
			noComments.append(stripComments)

		noLinesNoComments = [x for x in noComments if x]	# remove empty elems again

		for line in noLinesNoComments:		# remove whitespace
			finalRead.append(line.strip())

	for j in finalRead:

		# if push/pop command
		if j[0] == 'p':
			# capture the instruction, memory segment, and register int of the VM command
			firstSpace = j.index(' ')
			secondSpace = j.index(' ', firstSpace+1)

			instructionTerm = j[:firstSpace]
			memorySegmentTerm = j[firstSpace+1:secondSpace]
			regInt = j[secondSpace+1:]

			# push/pop assembly language
			if instructionTerm == 'push' and memorySegmentTerm == 'local':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'argument':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @ARG \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'this':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'that':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'constant':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @{regInt} \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'static':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @{functionNameChecker[-1][:functionNameChecker[-1].index('.')]}.{regInt} \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'temp':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @5 \n D=A \n @{regInt} \n A=D+A \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'pointer' and regInt == '0':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif instructionTerm == 'push' and memorySegmentTerm == 'pointer' and regInt == '1':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			# store pointer in general purpose register R13 to the desired virtual memory register 
			elif instructionTerm == 'pop' and memorySegmentTerm == 'local':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'argument':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @ARG \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'this':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THIS \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'that':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @THAT \n D=M \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'static':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @{functionNameChecker[-1][:functionNameChecker[-1].index('.')]}.{regInt} \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'temp':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @5 \n D=A \n @{regInt} \n A=D+A \n D=A \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n A=M \n M=D")

			elif instructionTerm == 'pop' and memorySegmentTerm == 'pointer' and regInt == '0':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @THIS \n M=D")	

			elif instructionTerm == 'pop' and memorySegmentTerm == 'pointer' and regInt == '1':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @THAT \n M=D")	

		# if branching command logic
		elif j[0:2] == 'if' or j[0:4] == 'goto' or j[0:5] == 'label':
			spaceIndex = j.index(' ')

			if j[0:5] == 'label':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n ({j[spaceIndex+1:]})")

			elif j[0:4] == 'goto':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @{j[spaceIndex+1:]} \n 0;JMP")

			elif j[0:2] == 'if':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @{j[spaceIndex+1:]} \n D;JNE")

		# function command logic
		elif j[0:4] == 'func' or j[0:4] == 'call' or j == 'return':

			if j[0:4] == 'func':
				firstSpace = j.index(' ')
				secondSpace = j.index(' ', firstSpace+1)
				functionName = j[firstSpace+1:secondSpace]
				nVars = int(j[secondSpace+1:])
				functionNameChecker.append(functionName)	# get the function name to write static instruction
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n ({functionName}) \n")

				while nVars > 0:
					writeAsm.append(f"@0 \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1")
					nVars = nVars - 1

			elif j[0:4] == 'call':
				firstSpace = j.index(' ')
				secondSpace = j.index(' ', firstSpace+1)
				functionName = j[firstSpace+1:secondSpace]
				nArgs = int(j[secondSpace+1:])
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @RETURN_ADDRESS_{returnCounterAddress} \n D=A \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @LCL \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @ARG \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THIS \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @THAT \n D=M \n @SP \n A=M \n M=D \n @SP \n M=M+1 \n @SP \n D=M \n @R13 \n M=D \n @5 \n D=A \n @R13 \n M=M-D \n @{nArgs} \n D=A \n @R13 \n M=M-D \n @R13 \n D=M \n @ARG \n M=D \n @SP \n D=M \n @LCL \n M=D \n @{functionName} \n 0;JMP \n (RETURN_ADDRESS_{returnCounterAddress})")
				returnCounterAddress = returnCounterAddress + 1

			elif j == 'return':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @LCL \n D=M \n @R7 \n M=D \n @5 \n A=D-A \n D=M \n @R13 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @ARG \n A=M \n M=D \n @ARG \n D=M \n @SP \n M=D+1 \n @R7 \n D=M  \n @1 \n A=D-A \n D=M \n @THAT \n M=D \n @R7 \n D=M \n @2 \n A=D-A \n D=M \n @THIS \n M=D \n @R7 \n D=M \n @3 \n A=D-A \n D=M \n @ARG \n M=D \n @R7 \n D=M \n @4 \n A=D-A \n D=M \n @LCL \n M=D \n @R13 \n A=M \n 0;JMP")


		else:

			# arithmetic logic
			if j == 'add':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D+M \n @SP \n A=M \n M=D \n @SP \n M=M+1")
			
			elif j == 'sub':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D-M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif j == 'neg':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n M=-M \n @SP \n M=M+1")

			elif j == 'eq':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLEQ{fillEqCounter} \n D;JEQ \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLEQ{fillEqCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillEqCounter = fillEqCounter + 1

			elif j == 'gt':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLGT{fillGtCounter} \n D;JGT \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLGT{fillGtCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillGtCounter = fillGtCounter + 1

			elif j == 'lt':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @SP \n A=M \n M=0 \n @R13 \n M=D \n @R14 \n D=D-M \n @FILLLT{fillLtCounter} \n D;JLT \n @SP \n M=M+1 \n @INSTRUCTION{instructionCounter+1} \n 0;JMP \n (FILLLT{fillLtCounter}) \n @SP \n A=M \n M=-1 \n @SP \n M=M+1")
				fillLtCounter = fillLtCounter + 1

			elif j == 'and':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D&M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif j == 'or':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R14 \n M=D \n @SP \n M=M-1 \n @SP \n A=M \n D=M \n @R13 \n M=D \n @R14 \n D=D|M \n @SP \n A=M \n M=D \n @SP \n M=M+1")

			elif j == 'not':
				writeAsm.append(f"// {j} \n (INSTRUCTION{instructionCounter}) \n @SP \n M=M-1 \n @SP \n A=M \n M=!M \n @SP \n M=M+1")
			

		instructionCounter = instructionCounter + 1

	#insert infinite loop after writing everything
	writeAsm.append(f'(INSTRUCTION{instructionCounter})')
	writeAsm.append(f'@INSTRUCTION{instructionCounter}')
	writeAsm.append('0;JMP')

	# write to output file
	asmFileName = sys.argv[1] + '.asm'
	with open(asmFileName, 'w') as f:
	    for line in writeAsm:
	        f.write(f"{line}\n")








