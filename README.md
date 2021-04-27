# tipy - Tiny Interpreter in Python

A tiny, toy programming language written in python

#### Input

```kotlin
fun f() {
    i = 0;
    fun g() {
        i = i + 1;
        print(i);
    }
    return g;
}

x = f();
y = f();
x();
y();
x();
y();
```

#### Output

```cpp
1.0
2.0
3.0
4.0
```

## Running

Execute `main.py` with the name of the script to be executed, with the extension of `.ti` at the end.
