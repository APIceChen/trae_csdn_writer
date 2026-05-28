# 原始文章内容

## 📋 文章元数据

| 属性 | 值 |
|------|-----|
| **标题** | 从 for 循环到 yield：一文搞懂 Python 迭代器与生成器 |
| **作者** | 未知作者 |
| **发布时间** | 最新推荐文章于 2026-05-26 11:28:04 发布 |
| **来源 URL** | https://blog.csdn.net/Nova_511/article/details/161144162 |
| **文章 ID** | 161144162 |
| **抓取时间** | 2026-05-28 17:01:59 |
| **抓取方式** | requests+BeautifulSoup |

## 📊 内容统计

- **字数**: 8340 字符
- **包含代码块**: ✅ 是
- **包含表格**: ❌ 否
- **包含图片**: ❌ 否

---

## 📝 正文内容

## 从 for 循环到 yield：一文搞懂 Python 迭代器与生成器

从 for 循环到 yield：一文搞懂 Python 迭代器与生成器
> 本文基于一个简单的 Python 示例，系统梳理for循环、可迭代对象、迭代器、自定义迭代器以及生成器之间的关系。
本文基于一个简单的 Python 示例，系统梳理
`for`
for
循环、可迭代对象、迭代器、自定义迭代器以及生成器之间的关系。

### 前言

前言
在 Python 中，我们经常会写这样的代码：

```
nums = [1, 2, 3, 4, 5]

for num in nums:
    print(num)

```

nums
=
[
1
,
2
,
3
,
4
,
5
]
for
num
in
nums
:
print
(
num
)
这段代码看起来非常自然：从列表里一个一个取出数字，然后打印出来。
但如果继续往底层看，
`for`
for
循环并不是凭空知道“下一个元素是谁”的。它背后依赖的核心机制，其实就是
**迭代器**
迭代器
。
理解迭代器之后，我们就能更清楚地理解 Python 中很多常见概念，比如：

- 为什么列表、字符串、字典都可以被for遍历；
为什么列表、字符串、字典都可以被
`for`
for
遍历；
- iter()和next()到底在做什么；
`iter()`
iter()
和
`next()`
next()
到底在做什么；
- 自定义对象如何支持循环；
自定义对象如何支持循环；
- yield为什么能让普通函数变成生成器；
`yield`
yield
为什么能让普通函数变成生成器；
- 生成器为什么适合处理大量数据或延迟计算。
生成器为什么适合处理大量数据或延迟计算。

### for 循环背后的真实过程

for 循环背后的真实过程
先看一个普通的列表遍历：

```
nums = [1, 2, 3, 4, 5]

for num in nums:
    print(num)

```

nums
=
[
1
,
2
,
3
,
4
,
5
]
for
num
in
nums
:
print
(
num
)
表面上看，
`for`
for
循环会自动从
`nums`
nums
中取值。但它的底层逻辑大致可以理解为下面这样：

```
nums = [1, 2, 3, 4, 5]
iter_obj = iter(nums)

while True:
    try:
        next_num = next(iter_obj)
        print(next_num)
    except StopIteration:
        break

```

nums
=
[
1
,
2
,
3
,
4
,
5
]
iter_obj
=
iter
(
nums
)
while
True
:
try
:
next_num
=
next
(
iter_obj
)
print
(
next_num
)
except
StopIteration
:
break
这里出现了两个非常关键的函数：

- iter()：把一个可迭代对象转换成迭代器；
`iter()`
iter()
：把一个可迭代对象转换成迭代器；
- next()：从迭代器中取出下一个值。
`next()`
next()
：从迭代器中取出下一个值。
当数据取完以后，迭代器会抛出
`StopIteration`
StopIteration
异常。
`for`
for
循环内部会捕获这个异常，然后结束循环。
所以，
`for`
for
循环的本质可以概括为：
> 先调用iter()得到迭代器，再不断调用next()取值，直到遇到StopIteration为止。
先调用
`iter()`
iter()
得到迭代器，再不断调用
`next()`
next()
取值，直到遇到
`StopIteration`
StopIteration
为止。

### 可迭代对象和迭代器的区别

可迭代对象和迭代器的区别
在讲迭代器之前，很容易把两个概念混在一起：

- 可迭代对象；
可迭代对象；
- 迭代器。
迭代器。
它们看起来很像，但并不是同一个东西。

### 什么是可迭代对象

什么是可迭代对象
可迭代对象指的是可以被
`iter()`
iter()
处理的对象。
常见的可迭代对象包括：

```
list
tuple
dict
set
str
range

```

list
tuple
dict
set
str
range
比如列表就是一个可迭代对象：

```
nums = [1, 2, 3]
iter_obj = iter(nums)

```

nums
=
[
1
,
2
,
3
]
iter_obj
=
iter
(
nums
)
只要一个对象实现了
`__iter__()`
__iter__()
方法，它通常就可以被称为可迭代对象。

### 什么是迭代器

什么是迭代器
迭代器是可以被
`next()`
next()
不断取值的对象。
一个标准的迭代器通常需要实现两个方法：

```
__iter__()
__next__()

```

__iter__
(
)
__next__
(
)
其中：

- __iter__()返回迭代器对象本身；
`__iter__()`
__iter__()
返回迭代器对象本身；
- __next__()返回下一个值；
`__next__()`
__next__()
返回下一个值；
- 如果没有更多数据，就抛出StopIteration。
如果没有更多数据，就抛出
`StopIteration`
StopIteration
。
换句话说：
> 可迭代对象负责“可以被遍历”，迭代器负责“真正一个一个吐出数据”。
可迭代对象负责“可以被遍历”，迭代器负责“真正一个一个吐出数据”。

### 自定义一个迭代器

自定义一个迭代器
下面我们自己实现一个简单的迭代器，让它依次返回
`1`
1
到
`5`
5
：

```
class MyIter:
    def __init__(self):
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.count <= 5:
            return self.count
        else:
            raise StopIteration("没有数据了")

```

class
MyIter
:
def
__init__
(
self
)
:
self
.
count
=
0
def
__iter__
(
self
)
:
return
self
def
__next__
(
self
)
:
self
.
count
+=
1
if
self
.
count
<=
5
:
return
self
.
count
else
:
raise
StopIteration
(
"没有数据了"
)
使用方式如下：

```
my_iter = MyIter()
my_iter_obj = iter(my_iter)

num1 = next(my_iter_obj)
num2 = next(my_iter_obj)
num3 = next(my_iter_obj)

print(num1, num2, num3)

```

my_iter
=
MyIter
(
)
my_iter_obj
=
iter
(
my_iter
)
num1
=
next
(
my_iter_obj
)
num2
=
next
(
my_iter_obj
)
num3
=
next
(
my_iter_obj
)
print
(
num1
,
num2
,
num3
)
输出结果是：

```
1 2 3

```

1 2 3
这个类的核心在于
`self.count`
self.count
。
它负责记录当前迭代到哪里了。每次调用
`next()`
next()
时，
`__next__()`
__next__()
方法都会让
`count`
count
加一，然后返回当前值。
当
`count`
count
超过
`5`
5
时，就说明数据已经取完，于是抛出
`StopIteration`
StopIteration
。
这也说明了迭代器的一个重要特点：
> 迭代器是有状态的，它会记住当前遍历到的位置。
迭代器是有状态的，它会记住当前遍历到的位置。

### 用 for 循环遍历自定义迭代器

用 for 循环遍历自定义迭代器
既然
`MyIter`
MyIter
已经实现了
`__iter__()`
__iter__()
和
`__next__()`
__next__()
，那么它也可以直接用于
`for`
for
循环：

```
for num in MyIter():
    print(num)

```

for
num
in
MyIter
(
)
:
print
(
num
)
输出结果：

```
1
2
3
4
5

```

1
2
3
4
5
这再次证明了前面的结论：
`for`
for
循环本质上就是在调用迭代器协议。
只要一个对象遵守这个协议，它就能被
`for`
for
循环消费。

### 迭代器的问题：写起来有点麻烦

迭代器的问题：写起来有点麻烦
虽然自定义迭代器的逻辑并不复杂，但完整写下来还是有些繁琐：

```
class MyIter:
    def __init__(self):
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.count <= 5:
            return self.count
        else:
            raise StopIteration

```

class
MyIter
:
def
__init__
(
self
)
:
self
.
count
=
0
def
__iter__
(
self
)
:
return
self
def
__next__
(
self
)
:
self
.
count
+=
1
if
self
.
count
<=
5
:
return
self
.
count
else
:
raise
StopIteration
为了返回几个值，我们要写类、写状态、写
`__iter__()`
__iter__()
、写
`__next__()`
__next__()
，还要手动处理
`StopIteration`
StopIteration
。
有没有更简单的写法？
有，这就是生成器。

### 生成器：用 yield 简化迭代器

生成器：用 yield 简化迭代器
生成器可以理解为一种更方便地创建迭代器的方式。
普通函数是这样的：

```
def func():
    print("开始执行了")

func()

```

def
func
(
)
:
print
(
"开始执行了"
)
func
(
)
调用
`func()`
func()
时，函数会立刻执行。
但如果函数中出现了
`yield`
yield
，情况就不一样了：

```
def func():
    print("开始执行了")
    yield 1

generator = func()

```

def
func
(
)
:
print
(
"开始执行了"
)
yield
1
generator
=
func
(
)
这时调用
`func()`
func()
并不会立刻执行函数体，而是返回一个生成器对象。
只有当我们调用
`next()`
next()
时，函数才会真正开始执行：

```
print(next(generator))

```

print
(
next
(
generator
)
)
执行过程是：

1. 进入函数；
进入函数；
1. 打印"开始执行了"；
打印
`"开始执行了"`
"开始执行了"
；
1. 遇到yield 1；
遇到
`yield 1`
yield 1
；
1. 暂停函数执行；
暂停函数执行；
1. 把1返回给调用方。
把
`1`
1
返回给调用方。
`yield`
yield
的关键点在于：它不仅返回值，还会暂停函数的执行状态。
下次继续调用
`next()`
next()
时，函数会从上一次暂停的位置继续往下执行。

### 用生成器生成随机数

用生成器生成随机数
比如我们想生成一百个
`1`
1
到
`100`
100
之间的随机数，可以这样写：

```
import random

def generator():
    for i in range(100):
        yield random.randint(1, 100)

for num in generator():
    print(num)

```

import
random
def
generator
(
)
:
for
i
in
range
(
100
)
:
yield
random
.
randint
(
1
,
100
)
for
num
in
generator
(
)
:
print
(
num
)
这里的
`generator()`
generator()
并不会一次性把一百个随机数全部创建出来。
它的执行方式是：

- for循环需要一个数；
`for`
for
循环需要一个数；
- 生成器运行到yield；
生成器运行到
`yield`
yield
；
- 返回一个随机数；
返回一个随机数；
- 暂停；
暂停；
- 下一轮循环再继续。
下一轮循环再继续。
这就是生成器的优势：
**按需生成，节省内存**
按需生成，节省内存
。
如果数据量很大，比如读取大文件、处理日志、生成无限序列，生成器会比一次性创建完整列表更合适。

### 迭代器和生成器的关系

迭代器和生成器的关系
可以这样理解：
> 生成器是一种特殊的迭代器。
生成器是一种特殊的迭代器。
生成器对象也可以被
`iter()`
iter()
处理，也可以被
`next()`
next()
取值。
例如：

```
def nums():
    yield 1
    yield 2
    yield 3

g = nums()

print(iter(g) is g)
print(next(g))
print(next(g))
print(next(g))

```

def
nums
(
)
:
yield
1
yield
2
yield
3
g
=
nums
(
)
print
(
iter
(
g
)
is
g
)
print
(
next
(
g
)
)
print
(
next
(
g
)
)
print
(
next
(
g
)
)
输出结果：

```
True
1
2
3

```

True
1
2
3
这说明生成器本身就是一个迭代器。
它帮我们省掉了手写
`__iter__()`
__iter__()
、
`__next__()`
__next__()
和状态管理的过程。

### 常见误区

常见误区

### 误区一：列表本身就是迭代器

误区一：列表本身就是迭代器
列表是可迭代对象，但列表本身不是迭代器。

```
nums = [1, 2, 3]

print(hasattr(nums, "__iter__"))   # True
print(hasattr(nums, "__next__"))   # False

```

nums
=
[
1
,
2
,
3
]
print
(
hasattr
(
nums
,
"__iter__"
)
)
# True
print
(
hasattr
(
nums
,
"__next__"
)
)
# False
列表可以被
`iter()`
iter()
转换成迭代器：

```
iter_obj = iter(nums)

print(hasattr(iter_obj, "__iter__"))  # True
print(hasattr(iter_obj, "__next__"))  # True

```

iter_obj
=
iter
(
nums
)
print
(
hasattr
(
iter_obj
,
"__iter__"
)
)
# True
print
(
hasattr
(
iter_obj
,
"__next__"
)
)
# True
所以更准确的说法是：
> 列表是可迭代对象，iter(列表)得到的对象才是迭代器。
列表是可迭代对象，
`iter(列表)`
iter(列表)
得到的对象才是迭代器。

### 误区二：yield 会立刻执行函数

误区二：yield 会立刻执行函数
包含
`yield`
yield
的函数被调用时，不会立刻执行函数体。

```
def func():
    print("开始执行了")
    yield 1

g = func()

```

def
func
(
)
:
print
(
"开始执行了"
)
yield
1
g
=
func
(
)
上面这段代码不会打印任何内容。
只有执行下面这行时，函数才会开始运行：

```
next(g)

```

next
(
g
)

### 误区三：StopIteration 是错误

误区三：StopIteration 是错误
`StopIteration`
StopIteration
并不一定代表程序出错。
在迭代器协议中，它是一种正常的结束信号。
当迭代器没有更多值时，就应该抛出
`StopIteration`
StopIteration
，告诉调用方“数据已经取完了”。
`for`
for
循环会自动处理这个异常，所以我们平时很少直接看到它。

### 小结

小结
本文从一个普通的
`for`
for
循环出发，逐步拆解了 Python 的迭代机制。
核心结论如下：

- for循环底层依赖iter()和next()；
`for`
for
循环底层依赖
`iter()`
iter()
和
`next()`
next()
；
- 可迭代对象是可以被iter()处理的对象；
可迭代对象是可以被
`iter()`
iter()
处理的对象；
- 迭代器是可以被next()不断取值的对象；
迭代器是可以被
`next()`
next()
不断取值的对象；
- 迭代器通过__iter__()和__next__()实现；
迭代器通过
`__iter__()`
__iter__()
和
`__next__()`
__next__()
实现；
- StopIteration用来表示迭代结束；
`StopIteration`
StopIteration
用来表示迭代结束；
- 生成器通过yield简化了迭代器的编写；
生成器通过
`yield`
yield
简化了迭代器的编写；
- 生成器按需生成数据，适合处理大数据量或延迟计算场景。
生成器按需生成数据，适合处理大数据量或延迟计算场景。
如果用一句话总结：
> 迭代器是 Python 循环机制的底层基础，而生成器是编写迭代器的优雅方式。
迭代器是 Python 循环机制的底层基础，而生成器是编写迭代器的优雅方式。

---

*本文由 CSDN AI Writer v1.2 自动抓取*
*抓取工具: csdn_scraper.py*
*保留原始格式，未经任何修改*
