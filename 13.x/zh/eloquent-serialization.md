# Eloquent：序列化

- [简介](#introduction)
- [模型与集合的序列化](#serializing-models-and-collections)
    - [序列化为数组](#serializing-to-arrays)
    - [序列化为 JSON](#serializing-to-json)
- [在 JSON 中隐藏属性](#hiding-attributes-from-json)
- [向 JSON 追加值](#appending-values-to-json)
- [日期序列化](#date-serialization)

<a name="introduction"></a>
## 简介

使用 Laravel 构建 API 时，你经常需要将模型及其关联转换为数组或 JSON。Eloquent 提供了便捷的方法来完成这些转换，同时让你能够控制模型的序列化表示中包含哪些属性。

> [!NOTE]
> 如果希望以更强大的方式处理 Eloquent 模型与集合的 JSON 序列化，请参阅 [Eloquent API 资源](/docs/{{version}}/eloquent-resources)文档。

<a name="serializing-models-and-collections"></a>
## 模型与集合的序列化

<a name="serializing-to-arrays"></a>
### 序列化为数组

要将模型及其已加载的[关联](/docs/{{version}}/eloquent-relationships)转换为数组，你应该使用 `toArray` 方法。该方法是递归的，因此所有属性和所有关联（包括关联的关联）都会被转换为数组：

```php
use App\Models\User;

$user = User::with('roles')->first();

return $user->toArray();
```

`attributesToArray` 方法可以将模型的属性转换为数组，但不包含模型的关联：

```php
$user = User::first();

return $user->attributesToArray();
```

你也可以在集合实例上调用 `toArray` 方法，将整个模型[集合](/docs/{{version}}/eloquent-collections)转换为数组：

```php
$users = User::all();

return $users->toArray();
```

<a name="serializing-to-json"></a>
### 序列化为 JSON

要将模型转换为 JSON，你应该使用 `toJson` 方法。与 `toArray` 一样，`toJson` 方法也是递归的，因此所有属性和关联都会被转换为 JSON。你还可以指定任何 [PHP 支持的](https://secure.php.net/manual/en/function.json-encode.php) JSON 编码选项：

```php
use App\Models\User;

$user = User::find(1);

return $user->toJson();

return $user->toJson(JSON_PRETTY_PRINT);
```

你也可以将模型或集合强制转换为字符串，这会自动调用模型或集合的 `toJson` 方法：

```php
return (string) User::find(1);
```

由于模型和集合在强制转换为字符串时会被转换为 JSON，你可以直接从应用的路由或控制器返回 Eloquent 对象。从路由或控制器返回 Eloquent 模型和集合时，Laravel 会自动将它们序列化为 JSON：

```php
Route::get('/users', function () {
    return User::all();
});
```

<a name="relationships"></a>
#### 关联

当 Eloquent 模型被转换为 JSON 时，已加载的关联会自动作为属性包含在 JSON 对象中。另外，虽然 Eloquent 关联方法使用「驼峰式」方法名定义，但关联的 JSON 属性名会使用「蛇形」命名。

<a name="hiding-attributes-from-json"></a>
## 在 JSON 中隐藏属性

有时，你可能希望限制模型的数组或 JSON 表示中包含的属性，例如隐藏密码。为此，你可以在模型上使用 `Hidden` 特性。列在 `Hidden` 特性中的属性不会包含在模型的序列化表示中：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Model;

#[Hidden(['password'])]
class User extends Model
{
    // ...
}
```


> [!NOTE]
> 要隐藏关联，请将关联方法名添加到 Eloquent 模型的 `Hidden` 特性中。

你也可以使用 `Visible` 特性，定义应包含在模型数组和 JSON 表示中的属性「允许列表」。将模型转换为数组或 JSON 时，未列在 `Visible` 特性中的所有属性都会被隐藏：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Visible;
use Illuminate\Database\Eloquent\Model;

#[Visible(['first_name', 'last_name'])]
class User extends Model
{
    // ...
}
```

<a name="temporarily-modifying-attribute-visibility"></a>
#### 临时修改属性可见性

如果希望让某些通常隐藏的属性在给定模型实例上可见，你可以使用 `makeVisible` 或 `mergeVisible` 方法。`makeVisible` 方法会返回模型实例：

```php
return $user->makeVisible('attribute')->toArray();

return $user->mergeVisible(['name', 'email'])->toArray();
```

同样，如果希望隐藏某些通常可见的属性，你可以使用 `makeHidden` 或 `mergeHidden` 方法：

```php
return $user->makeHidden('attribute')->toArray();

return $user->mergeHidden(['name', 'email'])->toArray();
```

如果想临时覆盖所有可见或隐藏的属性，你可以分别使用 `setVisible` 和 `setHidden` 方法：

```php
return $user->setVisible(['id', 'name'])->toArray();

return $user->setHidden(['email', 'password', 'remember_token'])->toArray();
```

<a name="appending-values-to-json"></a>
## 向 JSON 追加值

有时，将模型转换为数组或 JSON 时，你可能希望添加数据库中没有对应列的属性。要实现这一点，首先为该值定义一个[访问器](/docs/{{version}}/eloquent-mutators)：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 判断用户是否为管理员。
     */
    protected function isAdmin(): Attribute
    {
        return new Attribute(
            get: fn () => 'yes',
        );
    }
}
```

如果希望始终将访问器追加到模型的数组和 JSON 表示中，你可以在模型上使用 `Appends` 特性。注意，即使访问器的 PHP 方法使用「驼峰式」命名，引用属性名称时通常仍使用其「蛇形」序列化形式：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Appends;
use Illuminate\Database\Eloquent\Model;

#[Appends(['is_admin'])]
class User extends Model
{
    // ...
}
```

将属性添加到 `appends` 列表后，它就会包含在模型的数组和 JSON 表示中。`appends` 数组中的属性也会遵循模型上配置的 `visible` 和 `hidden` 设置。

<a name="appending-at-run-time"></a>
#### 运行时追加属性

运行时，你可以使用 `append` 或 `mergeAppends` 方法，让模型实例追加额外的属性。你也可以使用 `setAppends` 方法，覆盖给定模型实例的整个追加属性数组：

```php
return $user->append('is_admin')->toArray();

return $user->mergeAppends(['is_admin', 'status'])->toArray();

return $user->setAppends(['is_admin'])->toArray();
```

同样，如果希望移除模型的所有追加属性，你可以使用 `withoutAppends` 方法：

```php
return $user->withoutAppends()->toArray();
```

<a name="date-serialization"></a>
## 日期序列化

<a name="customizing-the-default-date-format"></a>
#### 自定义默认日期格式

你可以通过重写 `serializeDate` 方法，自定义默认的序列化格式。该方法不会影响日期存储到数据库时使用的格式：

```php
/**
 * 准备日期以用于数组 / JSON 序列化。
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

<a name="customizing-the-date-format-per-attribute"></a>
#### 为单个属性自定义日期格式

你可以在模型的[类型转换声明](/docs/{{version}}/eloquent-mutators#attribute-casting)中指定日期格式，为单个 Eloquent 日期属性自定义序列化格式：

```php
protected function casts(): array
{
    return [
        'birthday' => 'date:Y-m-d',
        'joined_at' => 'datetime:Y-m-d H:00',
    ];
}
```
