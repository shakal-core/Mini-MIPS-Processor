XOR $r1, $r0, $r0
NOR $r2, $r0, $r0
ADD $r3, $r0, $r0
SUB $r4, $r0, $r0
LW $r25, $r0, 15
SW $r5, $r0, 0
ADDI $r6, $r0, 10
SUBI $r7, $r0, 5
AND $r8, $r0, $r0
OR $r9, $r0, $r0
ANDI $r10, $r0, 15
ORI $r11, $r0, 3
SLL $r12, $r0, $r0
SRL $r13, $r0, $r0
J L15
L15: BEQ $r0, $r0, L16
L16: BNE $r0, $r0, END
END: ADD $r0, $r0, $r0