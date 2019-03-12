	.arch armv6
	.text
	.global regtest2
regtest2:
	push {r4, r5, r6, r7, r8, r9, r10, fp, r12, lr}
	mov fp, sp
	sub sp, sp, #432
	mov r5, r0
	bl getint
	mov r4, r0
	str r4, [fp, #-144]
	bl getint
	mov r4, r0
	str r4, [fp, #-140]
	cmp r5, #0
	ble L17
	ldr r4, [fp, #-144]
	add r4, r4, r5
	str r4, [fp, #-160]
	ldr r4, [fp, #-140]
	add r4, r4, r5
	str r4, [fp, #-156]
	b L21
L17:
	ldr r4, [fp, #-144]
	sub r4, r4, r5
	str r4, [fp, #-160]
	ldr r4, [fp, #-140]
	sub r4, r4, r5
	str r4, [fp, #-156]
L21:
	ldr r6, [fp, #-160]
	ldr r4, [fp, #-156]
	add r4, r6, r4
	str r4, [fp, #-136]
	bl getint
	mov r4, r0
	str r4, [fp, #-132]
	bl getint
	mov r6, r0
	ldr r4, [fp, #-132]
	cmp r4, r6
	ble L35
	ldr r4, [fp, #-132]
	add r4, r4, #1
	str r4, [fp, #-152]
	add r4, r6, #-1
	str r4, [fp, #-148]
	b L39
L35:
	ldr r4, [fp, #-132]
	add r4, r4, #1
	str r4, [fp, #-148]
	add r4, r6, #-1
	str r4, [fp, #-152]
L39:
	ldr r7, [fp, #-152]
	ldr r4, [fp, #-148]
	add r9, r7, r4
	bl getint
	mov r8, r0
	bl getint
	mov r12, r0
	cmp r8, r12
	ble L56
L53:
	bl getint
	mov r8, r0
	bl getint
	mov r12, r0
	cmp r8, r12
	bgt L53
L56:
	add r10, r8, r12
	add r7, r5, r10
	cmp r7, #0
	ble L78
	ldr r5, [fp, #-144]
	ldr r4, [fp, #-140]
	add r5, r5, r4
	ldr r4, [fp, #-160]
	add r5, r5, r4
	ldr r4, [fp, #-156]
	add r5, r5, r4
	ldr r4, [fp, #-136]
	add r5, r5, r4
	ldr r4, [fp, #-132]
	add r4, r5, r4
	add r5, r4, r6
	ldr r4, [fp, #-152]
	add r5, r5, r4
	ldr r4, [fp, #-148]
	add r4, r5, r4
	add r4, r4, r9
	add r4, r4, r8
	add r4, r4, r8
	add r4, r4, r10
	add r4, r4, r7
	b L97
L78:
	ldr r5, [fp, #-144]
	ldr r4, [fp, #-140]
	sub r5, r5, r4
	ldr r4, [fp, #-160]
	sub r5, r5, r4
	ldr r4, [fp, #-156]
	sub r5, r5, r4
	ldr r4, [fp, #-136]
	sub r5, r5, r4
	ldr r4, [fp, #-132]
	sub r4, r5, r4
	sub r5, r4, r6
	ldr r4, [fp, #-152]
	sub r5, r5, r4
	ldr r4, [fp, #-148]
	sub r4, r5, r4
	sub r4, r4, r9
	sub r4, r4, r8
	sub r4, r4, r8
	sub r4, r4, r10
	sub r4, r4, r7
L97:
	mov r0, r4
	add sp, sp, #432
	mov sp, fp
	pop {r4, r5, r6, r7, r8, r9, r10, fp, r12, pc}
