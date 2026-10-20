
# Eloquent: 修改器 & 类型转换

-   [介绍](#introduction)
-   [访问器和修改器](#accessors-and-mutators)
    -   [定义访问器](#defining-an-accessor)
    -   [定义修改器](#defining-a-mutator)
-   [属性类型转换](#attribute-casting)
    -   [数组和 JSON 转换](#array-and-json-casting)
    -   [日期转换](#date-casting)
    -   [枚举转换](#enum-casting)
    -   [加密转换](#encrypted-casting)
    -   [查询时转换](#query-time-casting)
-   [自定义转换](#custom-casts)
    -   [值对象转换](#value-object-casting)
    -   [数组 / JSON 序列化](#array-json-serialization)
    -   [入站转换](#inbound-casting)
    -   [转换参数](#cast-parameters)
    -   [可转换类](#castables)

## 介绍

访问器（Accessors）、修改器（Mutators）和属性类型转换（Attribute Casting）允许你在 **获取或设置 Eloquent 模型实例上的属性时** 对值进行转换。
例如，你可能希望使用 [Laravel 加密器](/docs/laravel/12.x/encryption) 在将值存储到数据库时对其加密，然后在通过 Eloquent 模型访问该属性时自动解密。
又或者，你可能希望将存储在数据库中的 JSON 字符串，在通过 Eloquent 模型访问时自动转换为数组。

## 访问器和修改器

### 定义访问器

访问器会在访问 Eloquent 属性值时对其进行转换。
要定义一个访问器，请在模型中创建一个 **受保护方法（protected method）** 来表示该可访问的属性。此方法名应当对应于底层模型属性 / 数据库列的 **驼峰命名（camel case）形式**（如果适用）。

在这个示例中，我们将为 `first_name` 属性定义一个访问器。
当尝试获取 `first_name` 属性的值时，Eloquent 会自动调用此访问器。
所有属性的访问器 / 修改器方法必须声明一个返回类型提示：`Illuminate\Database\Eloquent\Casts\Attribute`：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取用户的 first name
     */
    protected function firstName(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
        );
    }
}
```



所有访问器方法都会返回一个 `Attribute` 实例，它定义了该属性将如何被访问，以及（可选地）如何被修改。
在这个示例中，我们只定义了该属性如何被访问。
为此，我们向 `Attribute` 类的构造函数提供 `get` 参数。

如你所见，数据表列的原始值会传递给访问器，这样你就可以对其进行处理并返回。
要访问访问器的值，你只需在模型实例上访问 `first_name` 属性即可：

```php
use App\Models\User;

$user = User::find(1);

$firstName = $user->first_name;
```

> [!注意]
> 如果你希望这些计算后的值被添加到模型的 **数组 / JSON 表示中**，
> [你需要手动将它们追加](/docs/laravel/12.x/eloquent-serialization#appending-values-to-json)。

#### 从多个属性构建值对象 (Building Value Objects From Multiple Attributes)

有时，你的访问器可能需要将多个模型属性转换为单个“值对象（value object）”。
为此，你的 `get` 闭包可以接受第二个参数 `$attributes`，该参数会自动传入闭包中，并包含模型当前所有属性的数组：

```php
use App\Support\Address;
use Illuminate\Database\Eloquent\Casts\Attribute;

/**
 * 与用户的地址交互
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
    );
}
```

#### 访问器缓存 (Accessor Caching)

当从访问器返回值对象时，对该值对象所做的任何更改都会在模型保存之前自动同步回模型。
这是可能的，因为 **Eloquent 会保留访问器返回的实例**，以便在每次调用访问器时返回相同的实例：

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Line 1 Value';
$user->address->lineTwo = 'Updated Address Line 2 Value';

$user->save();
```



然而，有时你可能希望为 **原始值（primitive values）**（例如字符串和布尔值）启用缓存，尤其是在这些值的计算开销很大时。
要实现这一点，你可以在定义访问器时调用 `shouldCache` 方法：

```php
protected function hash(): Attribute
{
    return Attribute::make(
        get: fn (string $value) => bcrypt(gzuncompress($value)),
    )->shouldCache();
}
```

如果你想要 **禁用属性的对象缓存行为**，你可以在定义属性时调用 `withoutObjectCaching` 方法：

```php
/**
 * 与用户的地址交互
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
    )->withoutObjectCaching();
}
```

### 定义修改器 (Defining a Mutator)

修改器会在 **设置 Eloquent 属性值时** 对其进行转换。
要定义一个修改器，你可以在定义属性时提供 `set` 参数。

下面我们为 `first_name` 属性定义一个修改器。
当我们尝试在模型上设置 `first_name` 属性的值时，这个修改器会自动被调用：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 与用户的 first name 交互
     */
    protected function firstName(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
            set: fn (string $value) => strtolower($value),
        );
    }
}
```

修改器闭包会接收即将被设置到属性上的值，让你能够对该值进行处理并返回处理后的值。
要使用我们的修改器，我们只需要在 Eloquent 模型上设置 `first_name` 属性即可：

```php
use App\Models\User;

$user = User::find(1);

$user->first_name = 'Sally';
```



在这个示例中，`set` 回调会接收到值 `Sally`。
修改器随后会对该名称应用 `strtolower` 函数，并将其结果值设置到模型的内部 `$attributes` 数组中。

#### 修改多个属性 (Mutating Multiple Attributes)

有时，你的修改器可能需要在底层模型上设置多个属性。
要实现这一点，你可以从 `set` 闭包中返回一个数组。
数组中的每个键都应对应于模型的底层属性 / 数据表列：

```php
use App\Support\Address;
use Illuminate\Database\Eloquent\Casts\Attribute;

/**
 * 与用户的地址交互
 */
protected function address(): Attribute
{
    return Attribute::make(
        get: fn (mixed $value, array $attributes) => new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two'],
        ),
        set: fn (Address $value) => [
            'address_line_one' => $value->lineOne,
            'address_line_two' => $value->lineTwo,
        ],
    );
}
```

## 属性类型转换 (Attribute Casting)

属性类型转换提供了与访问器和修改器类似的功能，
但它不需要你在模型上定义任何额外的方法。
相反，你可以通过模型的 `casts` 方法，方便地将属性转换为常见的数据类型。

`casts` 方法应返回一个数组，其中 **键是要进行类型转换的属性名称**，
而 **值是你希望将该列转换成的类型**。

支持的转换类型有：

<div class="content-list" markdown="1">

- `array`
- `AsUri::class`
- `AsStringable::class`
- `boolean`
- `collection`
- `date`
- `datetime`
- `immutable_date`
- `immutable_datetime`
- <code>decimal:&lt;precision&gt;</code>
- `double`
- `encrypted`
- `encrypted:array`
- `encrypted:collection`
- `encrypted:object`
- `float`
- `hashed`
- `integer`
- `object`
- `real`
- `string`
- `timestamp`

</div>



为了演示属性类型转换（attribute casting），让我们把数据库中以整数 (`0` 或 `1`) 存储的 `is_admin` 属性，转换为布尔值：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'is_admin' => 'boolean',
        ];
    }
}
```

在定义了该类型转换之后，`is_admin` 属性在被访问时将始终被转换为布尔值，
即使其底层在数据库中是以整数形式存储的：

```php
$user = App\Models\User::find(1);

if ($user->is_admin) {
    // ...
}
```

如果你需要在运行时临时添加一个新的类型转换，可以使用 `mergeCasts` 方法。
这些转换定义会被添加到模型上已经定义的任何转换中：

```php
$user->mergeCasts([
    'is_admin' => 'integer',
    'options' => 'object',
]);
```

> [!警告]
> 值为 `null` 的属性不会被转换。
> 此外，你 **绝对不应该** 定义一个与 **关系（relationship）名称相同** 的类型转换（或属性），
> 也不要给模型的 **主键（primary key）** 指定类型转换。

#### Stringable 类型转换 (Stringable Casting)

你可以使用 `Illuminate\Database\Eloquent\Casts\AsStringable` 转换类，
将模型属性转换为一个 [fluent 的 Illuminate\Support\Stringable 对象](/docs/laravel/12.x/strings#fluent-strings-method-list)：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\AsStringable;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'directory' => AsStringable::class,
        ];
    }
}
```



### 数组和 JSON 转换 (Array and JSON Casting)

当处理以 **序列化 JSON** 存储的列时，`array` 类型转换特别有用。
例如，如果你的数据库有一个 `JSON` 或 `TEXT` 字段类型，并且里面存储了序列化的 JSON，
那么在该属性上添加 `array` 转换后，当你在 Eloquent 模型上访问该属性时，
它会自动将该值反序列化为 **PHP 数组**：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'options' => 'array',
        ];
    }
}
```

一旦定义了该转换，你就可以访问 `options` 属性，
它会自动从 JSON 反序列化为 **PHP 数组**。
当你为 `options` 属性赋值时，传入的数组会自动序列化为 JSON 并存储到数据库中：

```php
use App\Models\User;

$user = User::find(1);

$options = $user->options;

$options['key'] = 'value';

$user->options = $options;

$user->save();
```

如果你想用更简洁的语法更新 JSON 属性中的某个字段，
你可以先 [将该属性设置为可批量赋值](/docs/laravel/12.x/eloquent#mass-assignment-json-columns)，
然后在调用 `update` 方法时使用 `->` 操作符：

```php
$user = User::find(1);

$user->update(['options->key' => 'value']);
```

#### JSON 和 Unicode (JSON and Unicode)

如果你希望将数组属性存储为 **带有未转义 Unicode 字符的 JSON**，
可以使用 `json:unicode` 类型转换：

```php
/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => 'json:unicode',
    ];
}
```



#### 数组对象和集合转换 (Array Object and Collection Casting)

虽然标准的 `array` 类型转换对许多应用来说已经足够了，但它也有一些缺点。
由于 `array` 转换返回的是 **原始类型（primitive type）**，因此无法直接修改数组的某个偏移量。
例如，下面的代码会触发一个 PHP 错误：

```php
$user = User::find(1);

$user->options['key'] = $value;
```

为了解决这个问题，Laravel 提供了一个 `AsArrayObject` 转换，
它会将你的 JSON 属性转换为 [ArrayObject](https://www.php.net/manual/en/class.arrayobject.php) 类。
这个特性是通过 Laravel 的 [自定义转换](#custom-casts) 实现的，
Laravel 能够智能地缓存并转换已修改的对象，从而使你能够修改单个偏移量，而不会触发 PHP 错误。

要使用 `AsArrayObject` 转换，只需将它分配给某个属性：

```php
use Illuminate\Database\Eloquent\Casts\AsArrayObject;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsArrayObject::class,
    ];
}
```

同样地，Laravel 还提供了一个 `AsCollection` 转换，
它会将你的 JSON 属性转换为一个 Laravel [Collection](/docs/laravel/12.x/collections) 实例：

```php
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::class,
    ];
}
```

如果你希望 `AsCollection` 转换实例化的是一个 **自定义集合类**，
而不是 Laravel 的基础集合类，你可以将集合类名作为转换参数传入：

```php
use App\Collections\OptionCollection;
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::using(OptionCollection::class),
    ];
}
```



`of` 方法可用于指示集合项应通过集合的 [mapInto 方法](/docs/laravel/12.x/collections#method-mapinto) 映射到给定的类：

```php
use App\ValueObjects\Option;
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::of(Option::class)
    ];
}
```

在将集合映射到对象时，该对象应当实现 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口，
以定义其实例如何序列化为 JSON 并存储到数据库中：

```php
<?php

namespace App\ValueObjects;

use Illuminate\Contracts\Support\Arrayable;
use JsonSerializable;

class Option implements Arrayable, JsonSerializable
{
    public string $name;
    public mixed $value;
    public bool $isLocked;

    /**
     * 创建一个新的 Option 实例
     */
    public function __construct(array $data)
    {
        $this->name = $data['name'];
        $this->value = $data['value'];
        $this->isLocked = $data['is_locked'];
    }

    /**
     * 将实例作为数组返回
     *
     * @return array{name: string, data: string, is_locked: bool}
     */
    public function toArray(): array
    {
        return [
            'name' => $this->name,
            'value' => $this->value,
            'is_locked' => $this->isLocked,
        ];
    }

    /**
     * 指定应序列化为 JSON 的数据
     *
     * @return array{name: string, data: string, is_locked: bool}
     */
    public function jsonSerialize(): array
    {
        return $this->toArray();
    }
}
```

### 日期转换 (Date Casting)

默认情况下，Eloquent 会将 `created_at` 和 `updated_at` 列转换为 [Carbon](https://github.com/briannesbitt/Carbon) 实例。
Carbon 扩展了 PHP 的 `DateTime` 类，并提供了许多实用方法。

你可以通过在模型的 `casts` 方法中定义额外的日期类型转换，来转换更多的日期属性。
通常，日期应使用 `datetime` 或 `immutable_datetime` 转换类型。



在定义 `date` 或 `datetime` 类型转换时，你还可以指定日期的格式。
这个格式会在 [模型序列化为数组或 JSON](/docs/laravel/12.x/eloquent-serialization) 时使用：

```php
/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'created_at' => 'datetime:Y-m-d',
    ];
}
```

当某列被转换为日期时，你可以将对应的模型属性值设置为 **UNIX 时间戳**、日期字符串 (`Y-m-d`)、日期时间字符串，或者 `DateTime` / `Carbon` 实例。
该日期的值会被正确转换并存储到数据库中。

你可以通过在模型上定义 `serializeDate` 方法，自定义所有模型日期的默认序列化格式。
这个方法不会影响日期在数据库中的存储格式：

```php
/**
 * 为数组 / JSON 序列化准备日期
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

如果你想指定 **实际存储到数据库中的日期格式**，
可以在模型上定义 `$dateFormat` 属性：

```php
/**
 * 模型日期列的存储格式
 *
 * @var string
 */
protected $dateFormat = 'U';
```

#### 日期转换、序列化与时区 (Date Casting, Serialization, and Timezones)

默认情况下，`date` 和 `datetime` 类型转换会将日期序列化为 **UTC ISO-8601 日期字符串**
(`YYYY-MM-DDTHH:MM:SS.uuuuuuZ`)，
无论你的应用 `timezone` 配置选项设置为何值。

强烈建议你始终使用这种序列化格式，并且通过不更改应用的 `timezone` 配置选项（保持默认 `UTC`）来将应用日期存储在 UTC 时区中。
在整个应用中一致使用 UTC 时区，可以确保与你使用的 PHP 和 JavaScript 日期操作库的最大兼容性。



如果对 `date` 或 `datetime` 类型转换应用了自定义格式，例如 `datetime:Y-m-d H:i:s`，
则在日期序列化过程中会使用 **Carbon 实例的内部时区**。
通常，这会是你应用 `timezone` 配置选项中指定的时区。
然而，需要注意的是，像 `created_at` 和 `updated_at` 这样的 `timestamp` 列不受此行为影响，
它们始终以 **UTC** 格式化，而不管应用的时区设置如何。

### 枚举转换 (Enum Casting)

Eloquent 还允许你将属性值转换为 PHP [枚举 (Enums)](https://www.php.net/manual/en/language.enumerations.backed.php)。
为此，你可以在模型的 `casts` 方法中指定要转换的属性及对应的枚举类：

```php
use App\Enums\ServerStatus;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'status' => ServerStatus::class,
    ];
}
```

在模型上定义了枚举类型转换后，
当你与该属性交互时，它会自动在枚举与原始值之间进行转换：

```php
if ($server->status == ServerStatus::Provisioned) {
    $server->status = ServerStatus::Ready;

    $server->save();
}
```

#### 转换枚举数组 (Casting Arrays of Enums)

有时，你可能希望模型在单个列中存储 **枚举值数组**。
为此，你可以使用 Laravel 提供的 `AsEnumArrayObject` 或 `AsEnumCollection` 转换：

```php
use App\Enums\ServerStatus;
use Illuminate\Database\Eloquent\Casts\AsEnumCollection;

/**
 * 获取需要进行类型转换的属性
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'statuses' => AsEnumCollection::of(ServerStatus::class),
    ];
}
```



### 加密转换 (Encrypted Casting)

`encrypted` 类型转换会使用 Laravel 内置的 [加密功能](/docs/laravel/12.x/encryption) 对模型属性值进行加密。
此外，`encrypted:array`、`encrypted:collection`、`encrypted:object`、`AsEncryptedArrayObject` 和 `AsEncryptedCollection` 转换的行为与未加密版本类似；
然而，如你所料，当存储到数据库时，底层值会被加密。

由于加密后的文本长度不可预测，并且通常比原文长，
请确保相关数据库列的类型为 `TEXT` 或更大。
此外，由于值在数据库中被加密，你将无法直接查询或搜索加密属性的值。

#### 密钥轮换 (Key Rotation)

如你所知，Laravel 使用应用 `app` 配置文件中指定的 `key` 配置值来加密字符串。
通常，这个值对应于环境变量 `APP_KEY` 的值。
如果你需要轮换应用的加密密钥，则需要使用新密钥手动重新加密已加密的属性。

### 查询时转换 (Query Time Casting)

有时，你可能需要在执行查询时应用类型转换，例如在从表中选择原始值时。
例如，考虑以下查询：

```php
use App\Models\Post;
use App\Models\User;

$users = User::select([
    'users.*',
    'last_posted_at' => Post::selectRaw('MAX(created_at)')
        ->whereColumn('user_id', 'users.id')
])->get();
```

该查询结果中的 `last_posted_at` 属性将只是一个普通字符串。
如果我们能够在执行查询时对这个属性应用 `datetime` 类型转换，那就非常方便了。
幸运的是，我们可以使用 `withCasts` 方法实现这一点：

```php
$users = User::select([
    'users.*',
    'last_posted_at' => Post::selectRaw('MAX(created_at)')
        ->whereColumn('user_id', 'users.id')
])->withCasts([
    'last_posted_at' => 'datetime'
])->get();
```



<a name="custom-casts"></a>
## 自定义类型转换

Laravel 有许多内置的很有用的转换类型；然而，你有时可能需要定义自己的转换类型。要创建一个类型转换，请执行 `make:cast` Artisan 命令。新的转换类将放置在你的 `app/Casts` 目录中：

```shell
php artisan make:cast AsJson
```

所有自定义转换类都实现了 `CastsAttributes` 接口。实现此接口的类必须定义一个 `get` 和 `set` 方法。`get` 方法负责将数据库中的原始值变换为转换值，而 `set` 方法应该将转换值变换为可以存储在数据库中的原始值。作为一个例子，我们将内置的 `json` 转换类型重新实现为一个自定义转换类型：

```php
<?php

namespace App\Casts;

use Illuminate\Contracts\Database\Eloquent\CastsAttributes;
use Illuminate\Database\Eloquent\Model;

class AsJson implements CastsAttributes
{
    /**
     * 转换给定的值。
     *
     * @param  array<string, mixed>  $attributes
     * @return array<string, mixed>
     */
    public function get(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): array {
        return json_decode($value, true);
    }

    /**
     * 为存储准备给定的值。
     *
     * @param  array<string, mixed>  $attributes
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): string {
        return json_encode($value);
    }
}
```

一旦明确好一个自定义转换类型，你就可以使用其类名将其附加到模型属性上：

```php
<?php

namespace App\Models;

use App\Casts\AsJson;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取应类型转换的属性。
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'options' => AsJson::class,
        ];
    }
}
```



<a name="value-object-casting"></a>
### 值对象类型转换

不限于将值转换为原始类型，你还可以将值转换为对象。定义将值转换为对象的自定义转换与转换为原始类型非常相似；但是，`set` 方法应返回一个键 / 值对数组，这些键 / 值对将用于在模型上设置原始的可存储值。

作为一个例子，我们将定义一个自定义转换类，该类将多个模型值转换为一个 `Address` 值对象。我们假设 `Address` 值对象有两个公共属性：`lineOne` 和 `lineTwo` ：

```php
<?php

namespace App\Casts;

use App\ValueObjects\Address;
use Illuminate\Contracts\Database\Eloquent\CastsAttributes;
use Illuminate\Database\Eloquent\Model;
use InvalidArgumentException;

class AsAddress implements CastsAttributes
{
    /**
     * 转换给定的值。
     *
     * @param  array<string, mixed>  $attributes
     */
    public function get(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): Address {
        return new Address(
            $attributes['address_line_one'],
            $attributes['address_line_two']
        );
    }

    /**
     * 存储准备给定的值。
     *
     * @param  array<string, mixed>  $attributes
     * @return array<string, string>
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): array {
        if (! $value instanceof Address) {
            throw new InvalidArgumentException('The given value is not an Address instance.');
        }

        return [
            'address_line_one' => $value->lineOne,
            'address_line_two' => $value->lineTwo,
        ];
    }
}
```

在类型转换为值对象时，对值对象所做的任何更改都会在模型保存之前自动同步回模型：

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Value';

$user->save();
```

> [! 注意]
> 如果你打算将包含值对象的 Eloquent 模型序列化为 JSON 或数组，你应该在值对象上实现 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口。


<a name="value-object-caching"></a>
#### 值对象缓存

解析转换为值对象的属性时，它们会被 Eloquent 缓存。因此，如果再次访问该属性，将返回相同的对象实例。

如果你想禁用自定义类型转换类的对象缓存行为，可以在自定义转换类上声明一个公共的 `withoutObjectCaching` 属性：

```php
class AsAddress implements CastsAttributes
{
    public bool $withoutObjectCaching = true;

    // ...
}
```

<a name="array-json-serialization"></a>
### 数组 / JSON 序列化

当使用 `toArray` 和 `toJson` 方法将 Eloquent 模型转换为数组或 JSON 时，只要你的自定义转换值对象有实现 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口，它们通常也会被序列化。可是，当使用第三方库提供的值对象时，你可能没有能力向对象添加这些接口。

因此，你可以指定你的自定义转换类用于负责序列化值对象。为此，你的自定义转换类应该实现 `Illuminate\Contracts\Database\Eloquent\SerializesCastableAttributes` 接口。该接口表明你的类应该包含一个 `serialize` 方法，该方法应返回值对象的序列化形式：

```php
/**
 * 获取值的序列化表示形式。
 *
 * @param  array<string, mixed>  $attributes
 */
public function serialize(
    Model $model,
    string $key,
    mixed $value,
    array $attributes,
): string {
    return (string) $value;
}
```

<a name="inbound-casting"></a>
### 入站类型转换

有时，你可能需要编写一个自定义转换类，该类仅转换正在设置到模型上的值，并且在从模型检索属性时不执行任何操作。


仅入站的自定义转换应实现 `CastsInboundAttributes` 接口，该接口仅需要定义一个 `set` 方法。调用带 `--inbound` 选项的 `make:cast` Artisan 命令来生成仅入站的转换类：

```shell
php artisan make:cast AsHash --inbound
```

仅入站转换的一个经典例子是「哈希」转换。例如，我们可以定义一个通过给定算法对入站值进行哈希处理的转换：

```php
<?php

namespace App\Casts;

use Illuminate\Contracts\Database\Eloquent\CastsInboundAttributes;
use Illuminate\Database\Eloquent\Model;

class AsHash implements CastsInboundAttributes
{
    /**
     * 创建一个新的类型转换类实例。
     */
    public function __construct(
        protected string|null $algorithm = null,
    ) {}

    /**
     * 为存储准备给定的值。
     *
     * @param  array<string, mixed>  $attributes
     */
    public function set(
        Model $model,
        string $key,
        mixed $value,
        array $attributes,
    ): string {
        return is_null($this->algorithm)
            ? bcrypt($value)
            : hash($this->algorithm, $value);
    }
}
```

<a name="cast-parameters"></a>
### 类型转换参数

当将自定义转换附加到模型时，可以通过使用 `:` 字符分隔类名称并将多个参数用逗号分隔来指定转换参数。参数将被传递给转换类的构造函数：

```php
/**
 * 获取应类型转换的属性。
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'secret' => AsHash::class.':sha256',
    ];
}
```

<a name="castables"></a>
### 可转换类

你可能想要允许应用程序的值对象定义它们自己的自定义转换类。你不需要将自定义转换类附加到模型上，而是可以附加一个实现了 `Illuminate\Contracts\Database\Eloquent\Castable` 接口的值对象类：

```php
use App\ValueObjects\Address;

protected function casts(): array
{
    return [
        'address' => Address::class,
    ];
}
```



实现 `Castable` 接口的对象必须定义一个 `castUsing` 方法，该方法返回负责从 `Castable` 类转换的自定义转换类类名：

```php
<?php

namespace App\ValueObjects;

use Illuminate\Contracts\Database\Eloquent\Castable;
use App\Casts\AsAddress;

class Address implements Castable
{
    /**
     * 获取在从/向此转换目标转换时要使用的转换类名称。
     *
     * @param  array<string, mixed>  $arguments
     */
    public static function castUsing(array $arguments): string
    {
        return AsAddress::class;
    }
}
```

当使用 `Castable` 类时，你仍然可以在 `casts` 方法定义中提供参数。参数将被传递给 `castUsing` 方法：

```php
use App\ValueObjects\Address;

protected function casts(): array
{
    return [
        'address' => Address::class.':argument',
    ];
}
```

<a name="anonymous-cast-classes"></a>
#### 可转换类和匿名转换类

通过将「可转换类」与 PHP 的[匿名类](https://www.php.net/manual/en/language.oop5.anonymous.php)结合，你可以将值对象及其转换逻辑定义为一个单一的可转换对象。为此，从值对象的 `castUsing` 方法返回一个匿名类。匿名类应实现 `CastsAttributes` 接口：

```php
<?php

namespace App\ValueObjects;

use Illuminate\Contracts\Database\Eloquent\Castable;
use Illuminate\Contracts\Database\Eloquent\CastsAttributes;

class Address implements Castable
{
    // ...

    /**
     * 获取在从/向此转换目标转换时要使用的转换类。
     *
     * @param  array<string, mixed>  $arguments
     */
    public static function castUsing(array $arguments): CastsAttributes
    {
        return new class implements CastsAttributes
        {
            public function get(
                Model $model,
                string $key,
                mixed $value,
                array $attributes,
            ): Address {
                return new Address(
                    $attributes['address_line_one'],
                    $attributes['address_line_two']
                );
            }

            public function set(
                Model $model,
                string $key,
                mixed $value,
                array $attributes,
            ): array {
                return [
                    'address_line_one' => $value->lineOne,
                    'address_line_two' => $value->lineTwo,
                ];
            }
        };
    }
}
```
