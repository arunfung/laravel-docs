
# Eloquent：序列化

- [简介](#introduction)
- [模型与集合的序列化](#serializing-models-and-collections)
  - [序列化为数组](#serializing-to-arrays)
  - [序列化为 JSON](#serializing-to-json)
- [在 JSON 中隐藏属性](#hiding-attributes-from-json)
- [在 JSON 中追加值](#appending-values-to-json)
- [日期序列化](#date-serialization)

<a name="introduction"></a>
## 简介

在使用 Laravel 构建 API 时，你经常需要将模型及其关系转换为数组或 JSON。Eloquent 提供了方便的方法来进行这些转换，同时也允许你控制模型序列化表示中包含哪些属性

> 如果你希望以更强大的方式处理 Eloquent 模型与集合的 JSON 序列化，可以查看 [Eloquent API 资源](/docs/laravel/12.x/eloquent-resources) 的文档。

## 模型与集合的序列化

### 序列化为数组

若要将模型及其已加载的 [关系](/docs/laravel/12.x/eloquent-relationships) 转换为数组，可使用 `toArray` 方法。该方法是递归的，因此所有属性和所有关系（包括关系的关系）都会被转换为数组：

```php
use App\Models\User;

$user = User::with('roles')->first();

return $user->toArray();
```

如果你只想转换模型的属性而不包含其关系，可以使用 `attributesToArray` 方法：

```php
$user = User::first();

return $user->attributesToArray();
```
你还可以通过对模型 [集合](/docs/laravel/12.x/eloquent-collections) 调用 `toArray` 方法，将整个集合转换为数组：

```php
$users = User::all();

return $users->toArray();
```

### 序列化为 JSON

若要将模型转换为 JSON，可使用 `toJson` 方法。与 `toArray` 类似，`toJson` 方法也是递归的，因此所有属性和关系都会被转换为 JSON。你也可以传递任何 [PHP 支持的 JSON 编码选项](https://secure.php.net/manual/en/function.json-encode.php)：

```php
use App\Models\User;

$user = User::find(1);

return $user->toJson();

return $user->toJson(JSON_PRETTY_PRINT);
```



或者，你也可以将模型或集合**类型转换为字符串**，这会自动调用模型或集合的 `toJson` 方法：

```php
return (string) User::find(1);
```

由于模型和集合转换为字符串时会变为 JSON，因此你可以直接从应用的路由或控制器返回 Eloquent 对象。当它们从路由或控制器返回时，Laravel 会自动将 Eloquent 模型和集合序列化为 JSON：

```php
Route::get('/users', function () {
    return User::all();
});
```

#### 关系

当 Eloquent 模型被转换为 JSON 时，它已加载的关系会自动作为属性包含在 JSON 对象中。另外，虽然 Eloquent 关系方法是使用「camel case」命名法，但关系在 JSON 中的属性名称将会被转换为「snake case」。

## 在 JSON 中隐藏属性

有时你可能希望限制某些属性（例如密码）包含在模型的数组或 JSON 表示中。为此，可以向模型添加 `$hidden` 属性。列在 `$hidden` 数组中的属性将在序列化表示中被排除：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 在序列化时应被隐藏的属性。
     *
     * @var array<string>
     */
    protected $hidden = ['password'];
}
```

> 若要隐藏关系，请将关系方法名称添加到 Eloquent 模型的 `$hidden` 属性中。

另外，也可以使用 `$visible` 属性定义应在模型数组和 JSON 表示中包含的「仅允许列表」属性。所有未列在 `$visible` 数组中的属性在转换为数组或 JSON 时将被隐藏：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 在数组表示中应可见的属性。
     *
     * @var array
     */
    protected $visible = ['first_name', 'last_name'];
}
```



#### 临时修改属性可见性

如果你希望让某些**通常被隐藏的属性**在某个模型实例中可见，可以使用 `makeVisible` 方法。该方法会返回模型实例：

```php
return $user->makeVisible('attribute')->toArray();
```

同样地，如果你希望**隐藏某些通常可见的属性**，可以使用 `makeHidden` 方法：

```php
return $user->makeHidden('attribute')->toArray();
```

如果你想要临时**覆盖所有可见或隐藏的属性**，可以分别使用 `setVisible` 和 `setHidden` 方法：

```php
return $user->setVisible(['id', 'name'])->toArray();

return $user->setHidden(['email', 'password', 'remember_token'])->toArray();
```

## 向 JSON 添加值

有时在将模型转换为数组或 JSON 时，你可能希望**添加一些在数据库中并没有对应字段的属性**。要实现这一点，首先需要为该值定义一个 [访问器（accessor）](/docs/laravel/12.x/eloquent-mutators)：

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

如果你希望该访问器在模型的数组或 JSON 表示中**始终被追加**，可以将该属性名称加入模型的 `$appends` 属性中。注意，属性名称通常使用其「snake case」序列化形式引用，即使该访问器在 PHP 方法中是以「camel case」定义的：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 在模型数组形式中应被追加的访问器。
     *
     * @var array
     */
    protected $appends = ['is_admin'];
}
```



一旦属性被添加到 `appends` 列表中，它将被包含在模型的数组和 JSON 表示中。`appends` 数组中的属性也会遵循模型上配置的 `visible` 和 `hidden` 设置。

#### 运行时追加属性

在运行时，你可以使用 `append` 方法指示某个模型实例追加额外的属性。或者，你也可以使用 `setAppends` 方法**覆盖整个追加属性数组**：

```php
return $user->append('is_admin')->toArray();

return $user->setAppends(['is_admin'])->toArray();
```

## 日期序列化

#### 自定义默认日期格式

你可以通过覆盖 `serializeDate` 方法来**自定义默认的序列化格式**。此方法不会影响日期在数据库中的存储格式，仅影响其被序列化为数组或 JSON 时的格式：

```php
/**
 * 准备日期以用于数组 / JSON 序列化。
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

#### 为单个属性自定义日期格式

你可以通过在模型的 [属性类型转换声明](/docs/laravel/12.x/eloquent-mutators#attribute-casting) 中指定日期格式，来为**单个 Eloquent 日期属性**自定义序列化格式：

```php
protected function casts(): array
{
    return [
        'birthday' => 'date:Y-m-d',
        'joined_at' => 'datetime:Y-m-d H:00',
    ];
}
```
