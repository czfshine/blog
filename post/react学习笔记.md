# JSX

一个语法糖，可以在javascript里面写类似html标签的代码。像这样:

```jsx
const a= <h1> hello world!</h1>
```

经过解析器（通常是ES6的babel）后，会变成标准的javascript代码：

```javascript
 React.createElement('h1', null, `hello world!`);
```

使用JSX时要注意以下几点：

* 因为是在javascript脚本里面写HTML标签，会遇到一些关键字冲突，比如`class`。所以在HTML这样写：

  ```html
  <h1 class ="test"> hello world!</h1>
  ```

  JSX要写成

  ```jsx
  <h1 ClassName ="test"> hello world!</h1>
  ```

* 要在JSX使用javascript变量，要用花括号包起来。

# 组件

组件可以认为是给一类DOM起个名字，同时绑定对应的处理函数。

声明一个组件有三种方法

```javascript
/*函数式*/
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
/*或者*/
let Welcome = (props) => 
	return <h1>Hello, {props.name}</h1>;
}
/*定义类*/
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
```

