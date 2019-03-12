	.arch armv6
	.text
	.global s_add2
s_add2:
	push {fp, lr}
	mov fp, sp
	sub sp, sp, #36
	add sp, sp, #36
	pop {fp, pc}
