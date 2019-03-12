# m2-rtl-to-assembly-rossluu
## Goals
### Wednesday
Get header info:
.arch
.text
.global
label


### Tuesday
operations:
* set mem DONE
* jump/cond jumps DONE
* code label DONE

additional basic ops:
* subtraction DONE
* multiplication DONE

features:
* lookup table instead of offset calculation DONE 

things to fix:
* offset calculation wrong in some areas, could be fixed with table (don't worry about this) DONE
* separate setting register r0 (physical) from setting register 105 (or greater) (virtual register) DONE
* fix call insn indexing (two cases, one where saved to r0  (see helloworld2) and one where not saved at all (see addwithprint)) DONE

* seg faults when running with fib...