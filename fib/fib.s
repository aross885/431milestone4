	.arch armv6
	.text
	.global main
main:
	push {fp, lr}
	mov fp, sp
	sub sp, sp, #24
	mov r0, #10
	str r0, [fp, #-4]
