(module $arithmetic
  (func $add (param $left i32) (param $right i32) (result i32)
    local.get $left
    local.get $right
    i32.add)

  (func $twice (param $value i32) (result i32)
    local.get $value
    local.get $value
    call $add)

  (func $numeric (result i32)
    i32.const 20
    i32.const 22
    call 0)

  (func (result i32)
    i32.const 7)

  (export "twice" (func $twice)))
