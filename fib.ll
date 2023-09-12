; ModuleID = "rinha"
target triple = "arm64-apple-darwin22.6.0"
target datalayout = ""

define void @"main"()
{
entry:
  %".2" = call i32 @"fib"(i32 10)
  %".3" = call i32 (i8*, ...) @"printf"(i8* getelementptr ([3 x i8], [3 x i8]* @".str", i32 0, i32 0), i32 %".2")
  ret void
}

define i32 @"fib"(i32 %"n")
{
entry:
  %"lt_tmp" = icmp slt i32 %"n", 2
  br i1 %"lt_tmp", label %"then", label %"else"
then:
  br label %"ifcont"
else:
  %"subtmp" = sub i32 %"n", 1
  %".5" = call i32 @"fib"(i32 %"subtmp")
  %"subtmp.1" = sub i32 %"n", 2
  %".6" = call i32 @"fib"(i32 %"subtmp.1")
  %"addtmp" = add i32 %".5", %".6"
  br label %"ifcont"
ifcont:
  %"iftmp" = phi  i32 [%"n", %"then"], [%"addtmp", %"else"]
  ret i32 %"iftmp"
}

declare i32 @"printf"(i8* %".1", ...)

@".str" = private constant [3 x i8] c"%d\0a"