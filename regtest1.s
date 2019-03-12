	.arch armv6
	.text
	.global regtest1
regtest1:
	push {r4, r5, r6, r7, r8, r9, r10, fp, r12, lr}
	mov fp, sp
	sub sp, sp, #268
	mov r6, r0
	bl getint
	mov r4, r0
	str r4, [fp, #-120]
	bl getint
	mov r4, r0
	str r4, [fp, #-116]
	ldr r4, [fp, #-120]
	add r4, r4, r6
	str r4, [fp, #-112]
	ldr r4, [fp, #-116]
	add r4, r4, r6
	str r4, [fp, #-108]
	ldr r5, [fp, #-112]
	ldr r4, [fp, #-108]
	add r4, r5, r4
	str r4, [fp, #-104]
	bl getint
	mov r4, r0
	str r4, [fp, #-100]
	bl getint
	mov r4, r0
	str r4, [fp, #-96]
	ldr r4, [fp, #-100]
	add r9, r4, #1
	ldr r4, [fp, #-96]
	add r10, r4, #-1
	add r8, r9, r10
	bl getint
	mov r7, r0
	bl getint
	mov r4, r0
	add r12, r7, r4
	ldr r5, [fp, #-120]
	ldr r4, [fp, #-116]
	add r5, r5, r4
	ldr r4, [fp, #-112]
	add r5, r5, r4
	ldr r4, [fp, #-108]
	add r5, r5, r4
	ldr r4, [fp, #-104]
	add r5, r5, r4
	ldr r4, [fp, #-100]
	add r5, r5, r4
	ldr r4, [fp, #-96]
	add r4, r5, r4
	add r4, r4, r9
	add r4, r4, r10
	add r4, r4, r8
	add r4, r4, r7
	add r4, r4, r7
	add r5, r4, r12
	add r4, r6, r12
	add r4, r5, r4
	mov r0, r4
	str r0, [fp, #-64]
	mov r4, r4
	add sp, sp, #268
	mov sp, fp
	pop {r4, r5, r6, r7, r8, r9, r10, fp, r12, pc}
