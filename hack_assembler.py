# hack assembler for the Nand2Tetris course
# input = sys.argv[1] == xxx.asm; output = sys.argv[2] == xxx.hack
# xxx.hack file will consist of working machine language code

import sys

# initialize symbol table with pre-defined symbols
symbolTable = {
	"R0": 0,
	"R1": 1,
	"R2": 2,
	"R3": 3,
	"R4": 4,
	"R5": 5,
	"R6": 6,
	"R7": 7,
	"R8": 8,
	"R9": 9,
	"R10": 10,
	"R11": 11,
	"R12": 12,
	"R13": 13,
	"R14": 14,
	"R15": 15,
	"SCREEN": 16384,
	"KBD": 24576,
	"SP": 0,
	"LCL": 1,
	"ARG": 2,
	"THIS": 3,
	"THAT": 4
}
noComments = []
finalRead = []
indexA = []
indexC = []
instructionAInt = []
binaryAInstructions = []
binaryAInstructionSixteenBit = []
instructionC = []
instructionCBinary = []
writtenInstructions = []

sep = "//"

with open(sys.argv[1]) as f:
     lines = [line.rstrip('\n') for line in f]	# append each line into a list

noEmptyLines = [x for x in lines if x]	# remove empty elems
for line in noEmptyLines:						# remove comments
	stripComments = line.split(sep, 1)[0]
	noComments.append(stripComments)

noLinesNoComments = [x for x in noComments if x]	# remove empty elems again

for line in noLinesNoComments:		# remove whitespace
	finalRead.append(line.strip())

# first pass to add label symbols to symbol table
lineCounter = 0
for i in finalRead:
	if i[0] != '(':
		lineCounter += 1
	elif i[0] == '(':
		symbolTable[i[1:-1]] = lineCounter 

# second pass to add variable symbols to symbol table
n = 16
for i in finalRead:
	if i[0] == '@' and i[1:].isnumeric() == False and i[1:] not in symbolTable:
		symbolTable[i[1:]] = n 
		n += 1

for i in enumerate(finalRead):		# capture index of A & C-instructions
	if i[1][0] == '@':
		indexA.append(i[0])
	elif i[1][0] != '(':
		indexC.append(i[0])

for i in indexA:		# convert A-instruction strings to int
	if finalRead[i][1:].isnumeric() == True:
		instructionAInt.append(int(finalRead[i][1:]))
	elif finalRead[i][1:] in symbolTable:
		instructionAInt.append(symbolTable.get(finalRead[i][1:]))

for i in instructionAInt:		# convert A-instrucitons int to binary
	binaryAInstructions.append(bin(i)[2:])

for i in binaryAInstructions:		# convert binary A-instructions to 16-bit binary values
	binaryAInstructionSixteenBit.append(i.zfill(16))

for i in indexC:		# store C-Instructions
	instructionC.append(finalRead[i])

# initialize first 3 bits of C-instruction and binary value holder
firstThreeBits = '111'

# translate C-Instructions to binary values
for i in instructionC:
	
	# capture dest, comp, and jump if dest included in C-instruction
	if "=" in i:
		dest = i[:i.index('=')]
		if ";" in i:
			comp = i[i.index('=')+1:i.index(';')]
			jump = i[i.index(';')+1:]
		else:
			comp = i[i.index('=')+1:] 
			jump = 0
	# capture dest, comp, and jump if dest not included in C-Instruction
	else:
		dest = 0
		comp = i[:i.index(';')]
		jump = i[i.index(';')+1:]

	compBits = '0'
	destBits = '0'
	jumpBits = '0'

	# comp logic
	if comp == '0':
		compBits = '0101010'
	elif comp == '1':
		compBits = '0111111'
	elif comp == '-1':
		compBits = '0111010'
	elif comp == 'D':
		compBits = '0001100'
	elif comp == 'A':
		compBits = '0110000'
	elif comp == '!D':
		compBits = '0001101'
	elif comp == '!A':
		compBits = '0110001'
	elif comp == '-D':
		compBits = '0001111'
	elif comp == '-A':
		compBits = '0110011'
	elif comp == 'D+1':
		compBits = '0011111'
	elif comp == 'A+1':
		compBits = '0110111'
	elif comp == 'D-1':
		compBits = '0001110'
	elif comp == 'A-1':
		compBits = '0110010'
	elif comp =='D+A':
		compBits = '0000010'
	elif comp == 'D-A':
		compBits = '0010011'
	elif comp == 'A-D':
		compBits = '0000111'
	elif comp == 'D&A':
		compBits = '0000000'
	elif comp == 'D|A':
		compBits = '0010101'
	elif comp == 'M':
		compBits = '1110000'
	elif comp == '!M':
		compBits = '1110001'
	elif comp == '-M':
		compBits = '1110011'
	elif comp == 'M+1':
		compBits = '1110111'
	elif comp == 'M-1':
		compBits = '1110010'
	elif comp == 'D+M':
		compBits = '1000010'
	elif comp == 'D-M':
		compBits = '1010011'
	elif comp == 'M-D':
		compBits = '1000111'
	elif comp == 'D&M':
		compBits = '1000000'
	elif comp == 'D|M':
		compBits = '1010101'

	# dest logic
	if dest == 'M':
		destBits = '001'
	elif dest == 'D':
		destBits = '010'
	elif dest == 'MD':
		destBits = '011'
	elif dest == 'A':
		destBits = '100'
	elif dest == 'AM':
		destBits = '101'
	elif dest == 'AD':
		destBits = '110'
	elif dest == 'AMD':
		destBits = '111'
	else:
		destBits = '000'

	# jump logic
	if jump == 'JGT':
		jumpBits = '001'
	elif jump == 'JEQ':
		jumpBits = '010'
	elif jump == 'JGE':
		jumpBits = '011'
	elif jump == 'JLT':
		jumpBits = '100'
	elif jump == 'JNE':
		jumpBits = '101'
	elif jump == 'JLE':
		jumpBits = '110'
	elif jump == 'JMP':
		jumpBits = '111'
	else:
		jumpBits = '000'

	instructionCBits = firstThreeBits + compBits + destBits + jumpBits
	instructionCBinary.append(instructionCBits)

# rewrite the asm list with the newly translated binary Instructions
instructionACounter = 0
instructionCCounter = 0
for i in finalRead:
	if i[0] != '@' and i[0] != '(':
		writtenInstructions.append(instructionCBinary[instructionCCounter])
		instructionCCounter = instructionCCounter + 1
	elif i[0] == '@':
			writtenInstructions.append(binaryAInstructionSixteenBit[instructionACounter])
			instructionACounter = instructionACounter + 1

# write to output file
with open(sys.argv[2], 'w') as f:
    for line in writtenInstructions:
        f.write(f"{line}\n")










	