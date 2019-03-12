	.arch armv6
	.text
	.global main
main:
	push {fp, lr}
	mov fp, sp
	sub sp, sp, #56
	mov r0, #10
	str r0, [fp, #-24]
	ldr r1, [fp, #-24]
	str r1, [fp, #-24]
	mov r0, #200
	str r0, [fp, #-20]
	ldr r1, [fp, #-20]
	str r1, [fp, #-20]
	ldr r0, [fp, #-24]
	str r0, [fp, #-16]
	ldr r0, [fp, #-20]
	str r0, [fp, #-12]
	ldr r1, [fp, #-16]
	ldr r2, [fp, #-12]
	add r0, r1, r2
	str r0, [fp, #-36]
	ldr r1, [fp, #-36]
	mov r0, r1
	bl printint
	ldr r0, [fp, #-24]
	str r0, [fp, #-8]
	ldr r0, [fp, #-20]
	str r0, [fp, #-4]
	ldr r1, [fp, #-8]
	ldr r2, [fp, #-4]
	add r0, r1, r2
	str r0, [fp, #-32]
	ldr r1, [fp, #-32]
	mov r0, r1
	str r0, [fp, #-28]
	ldr r1, [fp, #-28]
	mov r0, r1
	mov sp, fp
	pop {fp, pc}
