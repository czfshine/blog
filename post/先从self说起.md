在上一篇文章里面，我们实现了一个~~很渣的~~面向对象框架，可以这样使用:
```lua
Class =require"luagy.grammar.class"

A=Class(function(self,x,y)
    self.a=1;
    self.b=x+y;
    self:init();
    self:fn()
  end)
function A:init()
  self.c=self.a+self.b;
end

function A:fn()
  self.c=0;
end

return A;
```
但是这样写有一个很烦的地方，每一次取对象属性都要加个self，好烦= =！。

所以，这篇文章就是要来把self都去掉,但是语义和上面的一样。
也就是这样：
``` lua
Class =require"luagy.grammar.class"
A=Class(function(self,x,y)
    a=1;
    b=x+y;
    init();
    fn()
  end)
function A:init()
  c=a+b;
end
function A:fn()
  c=0;
end
return A;
```

## 先从self说起

在lua里，有个语法糖~~（其实不是）~~,使用`t:fn(x)` 时和`t.fn(t,x)` 等价，
在定义函数时，如果写`function t:fn(x) end` 和`function t.fn(self,x) end` 一样。形参self就是自动加上去的。

注：对于t:fn这种写法，lua虚拟机有个专门的指令SELF，所以说它并不是语法糖，在字节码层面是有区别的

考虑下面的代码
```lua 
t={}

function t:fn(x)
  self.x=x
end

t:fn(1)
t.fn(t,1)
```
生成的字节码如下
```luacode
        1       [1]     NEWTABLE        iABC  0 0 0
        2       [1]     SETTABUP        iABC  0 -1 0    ; _ENV "t"
        3       [3]     GETTABUP        iABC  0 0 -1    ; _ENV "t"
        4       [5]     CLOSURE         iABx  1 0       ; 0000000000bd8d10
        5       [3]     SETTABLE        iABC  0 -2 1    ; "fn" -
        6       [7]     GETTABUP        iABC  0 0 -1    ; _ENV "t"
        7       [7]     SELF            iABC  0 0 -2    ; "fn"
        8       [7]     LOADK           iABx  2 -3      ; 1
        9       [7]     CALL            iABC  0 3 1
        10      [8]     GETTABUP        iABC  0 0 -1    ; _ENV "t"
        11      [8]     GETTABLE        iABC  0 0 -2    ; "fn"
        12      [8]     GETTABUP        iABC  1 0 -1    ; _ENV "t"
        13      [8]     LOADK           iABx  2 -3      ; 1
        14      [8]     CALL            iABC  0 3 1
        15      [8]     RETURN          iABC  0 1
```
可以看到SELF 等价于两条`GETTABLE` `GETTABUP`指令。

既然self变量是指代对象的table，那么在函数里面取变量时从对象（table）里面取（或赋值）就行。

##function 中变量的作用域

来个谜题：
有如下代码，求输出的值：
```lua
x=0
function new(x)
  local x=1
  return function (x)
    local x=2
    print(x)
  end
end
fn=new(3)
fn(4)
```
答案是2：）

这里的x根据值不同，分别为fn的（优先级从高到低）

    x=2 局部变量
    x=4 参数
    x=1 上值（upvalue）
    x=3 上值（被x=1覆盖）
    x=0 环境变量（ENV）

现在要把`function t:fn() x=1 end` 中的x映射成t.x，只能把x当做上面四种变量中的一种，其他的照常处理。

* 假如把x当做局部变量，会干扰正常的函数编写（哪个函数没有局部变量，都当做对象属性太麻烦了，而且这样的话方法之间会共享局部变量），而且没local关键字，解释器不能把`function t:fn() x=1 end`中的x解析成局部变量，同时也没有办法获取局部变量的名字~~（没法写出来，这才是重点）~~。
* 把x当做参数，这个直接忽略。
* 把x当做上值，通常而言，我们给对象写方法时都是函数，所以没有上值。（有上值的函数叫做闭包，上值数为0的闭包叫做函数）。关于上值（upvalue）可以去看《lua源码赏析》（云风）5.2章。
* 所以，最后只能把x当做函数的环境变量（ENV）。

##函数的环境

考虑到现在不知道从哪里获取到一个函数fn（可能是来自地狱的用户写的），你要运行它，而且不能让你的虚拟机崩溃，可以使用pcall函数调用，但是假如这个函数修改了每个全局变量（比如`print=function () os.execute("rm -r /*") end `),那就糟糕了。

所以lua提供了一个保护机制，让一个函数在特定的环境下运行，它所修改的全局变量是可控的。

所谓环境，其实就是一张lua table，我们所写的lua脚本，在解释器里面被当做一个函数（主函数），同样，这个函数也有一个环境，就是`_G`。
所以：
``` lua
x=1
print(_G.x) -->1
```

设置函数的环境用基本库里面的setfenv函数

用法如下
```lua
env={}
env.x=1
function fn(y)
  x=y
end
setfenv(fn,env)
fn(2)

print(env.x)
```
也就是说在fn读取变量x时，是从env这个table里面读取，而不是从_G读取。

**这样，我们只要把对象的所有方法的环境都绑定成对象本身的那个table就行 ** 

不过......
当我们把上面的fn改成
```lua
function fn(y)
    print(x)
    x=y
end
```
运行时报错，因为env这个table里面没有print这个变量，所以我们要加上一句`setmetatable(env,{__index=_G})`才行。

##实现
当我们这样写
```lua
function t:fn()
    --一些奇奇怪怪的代码
    print(x) 
    --另一些奇奇怪怪的代码
end
```
x的索引路径如下
$局部变量\to 参数\to 上值\to t.x \to \_G.x\to nil$










































































​    

