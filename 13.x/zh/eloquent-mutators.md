# Eloquent：修改器与类型转换

- [简介](#introduction)
- [访问器与修改器](#accessors-and-mutators)
    - [定义访问器](#defining-an-accessor)
    - [定义修改器](#defining-a-mutator)
- [属性类型转换](#attribute-casting)
    - [数组与 JSON 转换](#array-and-json-casting)
    - [向量转换](#vector-casting)
    - [二进制转换](#binary-casting)
    - [日期转换](#date-casting)
    - [枚举转换](#enum-casting)
    - [加密转换](#encrypted-casting)
    - [查询时转换](#query-time-casting)
- [自定义类型转换](#custom-casts)
    - [值对象转换](#value-object-casting)
    - [数组 / JSON 序列化](#array-json-serialization)
    - [入站转换](#inbound-casting)
    - [转换参数](#cast-parameters)
    - [比较转换后的值](#comparing-cast-values)
    - [可转换类](#castables)

<a name="introduction"></a>
## 简介

访问器、修改器和属性类型转换允许你在获取或设置模型实例的 Eloquent 属性时转换属性值。例如，你可能希望使用 [Laravel 加密器](/docs/{{version}}/encryption) 在将值存入数据库时对其加密，并在通过 Eloquent 模型访问该属性时自动解密。又或者，你希望通过 Eloquent 模型访问数据库中存储的 JSON 字符串时，将其转换为数组。

<a name="accessors-and-mutators"></a>
## 访问器与修改器

<a name="defining-an-accessor"></a>
### 定义访问器

访问器会在 Eloquent 属性被访问时转换其值。要定义访问器，请在模型中创建一个受保护方法，表示要访问的属性。如果该属性对应底层模型属性或数据库列，方法名应为该属性名或列名的驼峰形式。

在这个例子中，我们将为 `first_name` 属性定义访问器。尝试获取 `first_name` 属性值时，Eloquent 会自动调用该访问器。所有属性访问器 / 修改器方法都必须声明 `Illuminate\Database\Eloquent\Casts\Attribute` 返回类型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取用户的名字。
     */
    protected function firstName(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
        );
    }
}
```

所有访问器方法都返回一个 `Attribute` 实例，用于定义如何访问该属性，也可以定义如何修改它。在这个例子中，我们只定义属性的访问方式，因此向 `Attribute` 类的构造函数传入 `get` 参数。

如你所见，该列的原始值会传递给访问器，你可以对其进行处理并返回。要获取访问器的返回值，只需访问模型实例的 `first_name` 属性：

```php
use App\Models\User;

$user = User::find(1);

$firstName = $user->first_name;
```

> [!NOTE]
> 如果希望模型的数组 / JSON 表示包含这些计算后的值，[需要将它们追加到模型中](/docs/{{version}}/eloquent-serialization#appending-values-to-json)。

<a name="building-value-objects-from-multiple-attributes"></a>
#### 从多个属性构建值对象

有时，访问器需要将多个模型属性转换为一个「值对象」。为此，`get` 闭包可以接收第二个参数 `$attributes`。该参数会自动传入闭包，是一个包含模型当前所有属性的数组：

```php
use App\Support\Address;
use Illuminate\Database\Eloquent\Casts\Attribute;

/**
 * 与用户的地址交互。
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

<a name="accessor-caching"></a>
#### 访问器缓存

当访问器返回值对象时，对该对象所做的更改会在模型保存前自动同步回模型。这是因为 Eloquent 会保留访问器返回的实例，以便每次调用访问器时都返回同一个实例：

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Line 1 Value';
$user->address->lineTwo = 'Updated Address Line 2 Value';

$user->save();
```

有时，你也希望为字符串、布尔值等基本类型的值启用缓存，尤其是在这些值的计算开销较大时。为此，可以在定义访问器时调用 `shouldCache` 方法：

```php
protected function hash(): Attribute
{
    return Attribute::make(
        get: fn (string $value) => bcrypt(gzuncompress($value)),
    )->shouldCache();
}
```

如果希望禁用属性的对象缓存，可以在定义属性时调用 `withoutObjectCaching` 方法：

```php
/**
 * 与用户的地址交互。
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

<a name="defining-a-mutator"></a>
### 定义修改器

修改器会在 Eloquent 属性被赋值时转换其值。要定义修改器，可以在定义属性时传入 `set` 参数。下面为 `first_name` 属性定义一个修改器。当我们尝试设置模型的 `first_name` 属性值时，该修改器会被自动调用：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 与用户的名字交互。
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

修改器闭包会接收即将赋给属性的值，你可以处理该值并返回处理后的结果。要使用这个修改器，只需设置 Eloquent 模型的 `first_name` 属性：

```php
use App\Models\User;

$user = User::find(1);

$user->first_name = 'Sally';
```

在这个例子中，`set` 回调会接收到值 `Sally`。修改器随后对该名字调用 `strtolower` 函数，并将结果存入模型内部的 `$attributes` 数组。

<a name="mutating-multiple-attributes"></a>
#### 修改多个属性

有时，修改器需要设置底层模型的多个属性。为此，可以从 `set` 闭包返回一个数组。数组中的每个键都应对应模型的一个底层属性或数据库列：

```php
use App\Support\Address;
use Illuminate\Database\Eloquent\Casts\Attribute;

/**
 * 与用户的地址交互。
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

<a name="attribute-casting"></a>
## 属性类型转换

属性类型转换提供了与访问器、修改器类似的功能，而无需在模型上定义额外的方法。通过模型的 `casts` 方法，你可以方便地将属性转换为常见的数据类型。

`casts` 方法应返回一个数组，其中键为要转换的属性名，值为希望将该列转换成的类型。支持的转换类型如下：

<div class="content-list" markdown="1">

- `array`
- `AsFluent::class`
- `AsStringable::class`
- `AsUri::class`
- `AsVector::class`
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

为了演示属性类型转换，下面将数据库中以整数（`0` 或 `1`）存储的 `is_admin` 属性转换为布尔值：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性。
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

定义该转换后，访问 `is_admin` 属性时，它始终会转换为布尔值，即使数据库中存储的底层值是整数：

```php
$user = App\Models\User::find(1);

if ($user->is_admin) {
    // ...
}
```

如果需要在运行时临时添加新的类型转换，可以使用 `mergeCasts` 方法。这些转换定义会合并到模型已有的转换定义中：

```php
$user->mergeCasts([
    'is_admin' => 'integer',
    'options' => 'object',
]);
```

> [!WARNING]
> 值为 `null` 的属性不会进行类型转换。此外，不应定义与关联同名的类型转换（或属性），也不应为模型的主键指定类型转换。

<a name="stringable-casting"></a>
#### Stringable 转换

你可以使用 `Illuminate\Database\Eloquent\Casts\AsStringable` 转换类，将模型属性转换为[支持流式操作的 Illuminate\Support\Stringable 对象](/docs/{{version}}/strings#fluent-strings-method-list)：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Casts\AsStringable;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性。
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

<a name="array-and-json-casting"></a>
### 数组与 JSON 转换

处理存储序列化 JSON 的列时，`array` 转换尤其有用。例如，数据库中的 `JSON` 或 `TEXT` 字段存储了序列化的 JSON，为该属性添加 `array` 转换后，通过 Eloquent 模型访问该属性时，它会自动反序列化为 PHP 数组：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性。
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

定义转换后，访问 `options` 属性时，它会自动从 JSON 反序列化为 PHP 数组。设置 `options` 属性值时，传入的数组会自动重新序列化为 JSON 以便存储：

```php
use App\Models\User;

$user = User::find(1);

$options = $user->options;

$options['key'] = 'value';

$user->options = $options;

$user->save();
```

要用更简洁的语法更新 JSON 属性中的某个字段，可以[允许对该属性进行批量赋值](/docs/{{version}}/eloquent#mass-assignment-json-columns)，并在调用 `update` 方法时使用 `->` 操作符：

```php
$user = User::find(1);

$user->update(['options->key' => 'value']);
```

<a name="json-and-unicode"></a>
#### JSON 与 Unicode

如果希望将数组属性存储为 JSON，并保留未转义的 Unicode 字符，可以使用 `json:unicode` 转换：

```php
/**
 * 获取需要进行类型转换的属性。
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

<a name="array-object-and-collection-casting"></a>
#### 数组对象与集合转换

虽然标准的 `array` 转换能满足许多应用的需要，但也存在一些不足。由于 `array` 转换返回的是基本类型，无法直接修改数组中某个偏移量的值。例如，以下代码会触发 PHP 错误：

```php
$user = User::find(1);

$user->options['key'] = $value;
```

为解决这个问题，Laravel 提供了 `AsArrayObject` 转换，将 JSON 属性转换为 [ArrayObject](https://www.php.net/manual/en/class.arrayobject.php) 对象。该功能基于 Laravel 的[自定义转换](#custom-casts)实现，使 Laravel 能够缓存并转换修改后的对象，从而允许修改单个偏移量的值，而不会触发 PHP 错误。要使用 `AsArrayObject` 转换，只需将其指定给属性：

```php
use Illuminate\Database\Eloquent\Casts\AsArrayObject;

/**
 * 获取需要进行类型转换的属性。
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

同样，Laravel 提供了 `AsCollection` 转换，将 JSON 属性转换为 Laravel [Collection](/docs/{{version}}/collections) 实例：

```php
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性。
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

默认情况下，为使用 `AsArrayObject` 或 `AsCollection` 转换的属性赋值 `null`，会在数据库中存储 JSON `null` 值。如果希望将 `null` 存储为原生 SQL `NULL`，可以在定义转换时调用 `nullable` 方法：

```php
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性。
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'options' => AsCollection::nullable(),
    ];
}
```

`nullable` 方法也可以与自定义集合类结合使用：

```php
'options' => AsCollection::nullable(OptionCollection::class),
```

`AsArrayObject` 转换也提供了行为相同的 `nullable` 方法。

如果希望 `AsCollection` 转换实例化自定义集合类，而不是 Laravel 的基础集合类，可以将集合类名作为转换参数传入：

```php
use App\Collections\OptionCollection;
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性。
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

`of` 方法用于指定通过集合的 [mapInto 方法](/docs/{{version}}/collections#method-mapinto)，将集合项映射为给定类的实例：

```php
use App\ValueObjects\Option;
use Illuminate\Database\Eloquent\Casts\AsCollection;

/**
 * 获取需要进行类型转换的属性。
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

将集合项映射为对象时，该对象应实现 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口，定义其实例如何序列化为 JSON 并存入数据库：

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
     * 创建一个新的 Option 实例。
     */
    public function __construct(array $data)
    {
        $this->name = $data['name'];
        $this->value = $data['value'];
        $this->isLocked = $data['is_locked'];
    }

    /**
     * 将实例转换为数组。
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
     * 指定要序列化为 JSON 的数据。
     *
     * @return array{name: string, data: string, is_locked: bool}
     */
    public function jsonSerialize(): array
    {
        return $this->toArray();
    }
}
```

<a name="vector-casting"></a>
### 向量转换

你可以使用 `Illuminate\Database\Eloquent\Casts\AsVector` 转换类，在数据库向量列与 PHP 数组之间进行转换：

```php
use Illuminate\Database\Eloquent\Casts\AsVector;

/**
 * 获取需要进行类型转换的属性。
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'embedding' => AsVector::class,
    ];
}
```

设置属性时，该转换接受 PHP 数组或 `Arrayable` 实例，例如 Laravel 集合。获取属性时，该转换返回一个浮点数数组。

<a name="binary-casting"></a>
### 二进制转换

如果 Eloquent 模型除了自增 ID 列外，还有一个[二进制类型](/docs/{{version}}/migrations#column-method-binary)的 `uuid` 或 `ulid` 列，可以使用 `AsBinary` 转换，在属性值与其二进制表示之间自动进行转换：

```php
use Illuminate\Database\Eloquent\Casts\AsBinary;

/**
 * 获取需要进行类型转换的属性。
 *
 * @return array<string, string>
 */
protected function casts(): array
{
    return [
        'uuid' => AsBinary::uuid(),
        'ulid' => AsBinary::ulid(),
    ];
}
```

在模型上定义转换后，可以将 UUID / ULID 属性设置为对象实例或字符串，Eloquent 会自动将其转换为二进制表示。获取该属性值时，始终会得到明文字符串：

```php
use Illuminate\Support\Str;

$user->uuid = Str::uuid();

return $user->uuid;

// "6e8cdeed-2f32-40bd-b109-1e4405be2140"
```

<a name="date-casting"></a>
### 日期转换

默认情况下，Eloquent 会将 `created_at` 和 `updated_at` 列转换为 [Carbon](https://github.com/briannesbitt/Carbon) 实例。Carbon 扩展了 PHP 的 `DateTime` 类，并提供了许多实用方法。你可以在模型的 `casts` 方法中添加日期转换定义，以转换其他日期属性。通常应使用 `datetime` 或 `immutable_datetime` 类型转换日期。

定义 `date` 或 `datetime` 转换时，还可以指定日期格式。[模型序列化为数组或 JSON](/docs/{{version}}/eloquent-serialization) 时会使用该格式：

```php
/**
 * 获取需要进行类型转换的属性。
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

将列转换为日期后，可以将对应的模型属性设置为 UNIX 时间戳、日期字符串（`Y-m-d`）、日期时间字符串或 `DateTime` / `Carbon` 实例。日期值会被正确转换并存入数据库。

你可以在模型上定义 `serializeDate` 方法，自定义该模型所有日期的默认序列化格式。该方法不会影响日期存入数据库时使用的格式：

```php
/**
 * 为数组 / JSON 序列化准备日期。
 */
protected function serializeDate(DateTimeInterface $date): string
{
    return $date->format('Y-m-d');
}
```

要指定模型日期实际存入数据库时使用的格式，应使用模型的 `Table` 特性中的 `dateFormat` 参数：

```php
use Illuminate\Database\Eloquent\Attributes\Table;

#[Table(dateFormat: 'U')]
class Flight extends Model
{
    // ...
}
```

<a name="date-casting-and-timezones"></a>
#### 日期转换、序列化与时区

默认情况下，无论应用的 `timezone` 配置指定什么时区，`date` 和 `datetime` 转换都会将日期序列化为 UTC ISO-8601 日期字符串（`YYYY-MM-DDTHH:MM:SS.uuuuuuZ`）。强烈建议始终使用这种序列化格式，并将应用的 `timezone` 配置保持为默认值 `UTC`，以 UTC 时区存储应用中的日期。在整个应用中统一使用 UTC 时区，可以最大程度地兼容其他 PHP 和 JavaScript 日期处理库。

如果为 `date` 或 `datetime` 转换指定了自定义格式，例如 `datetime:Y-m-d H:i:s`，日期序列化时会使用 Carbon 实例内部的时区，通常就是应用的 `timezone` 配置所指定的时区。不过，`created_at` 和 `updated_at` 等 `timestamp` 列不受此行为影响，无论应用设置什么时区，它们始终以 UTC 格式化。

<a name="enum-casting"></a>
### 枚举转换

Eloquent 也允许将属性值转换为 PHP [枚举](https://www.php.net/manual/en/language.enumerations.backed.php)。为此，可以在模型的 `casts` 方法中指定要转换的属性及对应的枚举类：

```php
use App\Enums\ServerStatus;

/**
 * 获取需要进行类型转换的属性。
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

在模型上定义转换后，读取或设置指定属性时，它会自动在枚举与底层值之间进行转换：

```php
if ($server->status == ServerStatus::Provisioned) {
    $server->status = ServerStatus::Ready;

    $server->save();
}
```

<a name="casting-arrays-of-enums"></a>
#### 转换枚举数组

有时，你需要让模型在单个列中存储一组枚举值。为此，可以使用 Laravel 提供的 `AsEnumArrayObject` 或 `AsEnumCollection` 转换：

```php
use App\Enums\ServerStatus;
use Illuminate\Database\Eloquent\Casts\AsEnumCollection;

/**
 * 获取需要进行类型转换的属性。
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

<a name="encrypted-casting"></a>
### 加密转换

`encrypted` 转换使用 Laravel 内置的[加密功能](/docs/{{version}}/encryption)对模型属性值进行加密。此外，`encrypted:array`、`encrypted:collection`、`encrypted:object`、`AsEncryptedArrayObject` 和 `AsEncryptedCollection` 转换的行为与各自未加密的版本相同，只是在存入数据库时会对底层值进行加密。

由于加密文本的最终长度无法预测，且比对应的明文更长，请确保相关数据库列为 `TEXT` 或容量更大的类型。此外，由于这些值在数据库中是加密的，你无法查询或搜索加密属性的值。

<a name="key-rotation"></a>
#### 密钥轮换

Laravel 使用应用 `app` 配置文件中指定的 `key` 配置值加密字符串，该值通常对应 `APP_KEY` 环境变量。如果需要轮换应用的加密密钥，可以[平滑地完成轮换](/docs/{{version}}/encryption#gracefully-rotating-encryption-keys)。

<a name="query-time-casting"></a>
### 查询时转换

有时，你需要在执行查询时应用类型转换，例如从表中选取原始值时。以下面的查询为例：

```php
use App\Models\Post;
use App\Models\User;

$users = User::select([
    'users.*',
    'last_posted_at' => Post::selectRaw('MAX(created_at)')
        ->whereColumn('user_id', 'users.id')
])->get();
```

该查询结果中的 `last_posted_at` 属性只是一个普通字符串。如果能在执行查询时对该属性应用 `datetime` 转换，会更加方便。使用 `withCasts` 方法即可实现：

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

Laravel 内置了多种实用的转换类型，但有时你仍需要定义自己的转换类型。要创建转换类，请执行 `make:cast` Artisan 命令。新类会放在 `app/Casts` 目录中：

```shell
php artisan make:cast AsJson
```

所有自定义转换类都实现 `CastsAttributes` 接口。实现该接口的类必须定义 `get` 和 `set` 方法。`get` 方法负责将数据库中的原始值转换为目标值，`set` 方法则将转换后的值还原为可存入数据库的原始值。下面以自定义转换类型重新实现内置的 `json` 转换：

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
     * 将给定的值转换为可存储的形式。
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

定义自定义转换类型后，可以通过类名将其指定给模型属性：

```php
<?php

namespace App\Models;

use App\Casts\AsJson;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 获取需要进行类型转换的属性。
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
### 值对象转换

类型转换不仅限于基本类型，也可以将值转换为对象。定义对象转换与基本类型转换非常相似。不过，如果值对象涵盖多个数据库列，`set` 方法必须返回一个键值对数组，用于设置模型上可存储的原始值。如果值对象只涉及单个列，则直接返回可存储的值即可。

下面定义一个自定义转换类，将多个模型属性值转换为一个 `Address` 值对象。假设 `Address` 值对象具有 `lineOne` 和 `lineTwo` 两个公共属性：

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
     * 将给定的值转换为可存储的形式。
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

转换为值对象后，对该对象所做的更改会在模型保存前自动同步回模型：

```php
use App\Models\User;

$user = User::find(1);

$user->address->lineOne = 'Updated Address Value';

$user->save();
```

> [!NOTE]
> 如果要将包含值对象的 Eloquent 模型序列化为 JSON 或数组，应让值对象实现 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口。

<a name="value-object-caching"></a>
#### 值对象缓存

转换为值对象的属性在解析后会被 Eloquent 缓存。因此，再次访问该属性时会返回同一个对象实例。

如果希望禁用自定义转换类的对象缓存，可以在该类上声明公共属性 `withoutObjectCaching`：

```php
class AsAddress implements CastsAttributes
{
    public bool $withoutObjectCaching = true;

    // ...
}
```

<a name="array-json-serialization"></a>
### 数组 / JSON 序列化

使用 `toArray` 和 `toJson` 方法将 Eloquent 模型转换为数组或 JSON 时，只要自定义转换的值对象实现了 `Illuminate\Contracts\Support\Arrayable` 和 `JsonSerializable` 接口，通常也会一并序列化。不过，使用第三方库提供的值对象时，你可能无法为其添加这些接口。

因此，你可以让自定义转换类负责序列化值对象。为此，该类应实现 `Illuminate\Contracts\Database\Eloquent\SerializesCastableAttributes` 接口。该接口要求类中定义 `serialize` 方法，返回值对象的序列化形式：

```php
/**
 * 获取该值的序列化表示。
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
### 入站转换

有时，你需要编写一个自定义转换类，只在设置模型属性时转换传入的值，而在获取属性时不执行任何操作。

仅处理入站值的自定义转换应实现 `CastsInboundAttributes` 接口，该接口只要求定义 `set` 方法。执行 `make:cast` Artisan 命令时加上 `--inbound` 选项，即可生成仅处理入站值的转换类：

```shell
php artisan make:cast AsHash --inbound
```

「哈希」转换是仅处理入站值的典型例子。例如，可以定义一个转换，使用给定算法对传入值进行哈希处理：

```php
<?php

namespace App\Casts;

use Illuminate\Contracts\Database\Eloquent\CastsInboundAttributes;
use Illuminate\Database\Eloquent\Model;

class AsHash implements CastsInboundAttributes
{
    /**
     * 创建一个新的转换类实例。
     */
    public function __construct(
        protected string|null $algorithm = null,
    ) {}

    /**
     * 将给定的值转换为可存储的形式。
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
### 转换参数

将自定义转换指定给模型时，可以在类名后加上 `:` 来指定转换参数，多个参数之间用逗号分隔。这些参数会传给转换类的构造函数：

```php
/**
 * 获取需要进行类型转换的属性。
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

<a name="comparing-cast-values"></a>
### 比较转换后的值

如果希望自定义两个转换后的值的比较方式，以判断值是否发生变化，可以让自定义转换类实现 `Illuminate\Contracts\Database\Eloquent\ComparesCastableAttributes` 接口。这样便能精确控制模型更新时，Eloquent 将哪些值视为已更改并保存到数据库。

该接口要求类中定义 `compare` 方法，当给定的两个值被视为相等时返回 `true`：

```php
/**
 * 判断给定的值是否相等。
 *
 * @param  \Illuminate\Database\Eloquent\Model  $model
 * @param  string  $key
 * @param  mixed  $firstValue
 * @param  mixed  $secondValue
 * @return bool
 */
public function compare(
    Model $model,
    string $key,
    mixed $firstValue,
    mixed $secondValue
): bool {
    return $firstValue === $secondValue;
}
```

<a name="castables"></a>
### 可转换类

你可能希望让应用的值对象自行指定其自定义转换类。此时，可以在模型上指定实现了 `Illuminate\Contracts\Database\Eloquent\Castable` 接口的值对象类，而非直接指定自定义转换类：

```php
use App\ValueObjects\Address;

protected function casts(): array
{
    return [
        'address' => Address::class,
    ];
}
```

实现 `Castable` 接口的对象必须定义 `castUsing` 方法，返回自定义转换类的类名。该转换类负责在底层值与此 `Castable` 类之间进行转换：

```php
<?php

namespace App\ValueObjects;

use Illuminate\Contracts\Database\Eloquent\Castable;
use App\Casts\AsAddress;

class Address implements Castable
{
    /**
     * 获取用于在底层值与此转换目标之间进行转换的类名。
     *
     * @param  array<string, mixed>  $arguments
     */
    public static function castUsing(array $arguments): string
    {
        return AsAddress::class;
    }
}
```

使用 `Castable` 类时，仍可以在 `casts` 方法的定义中提供参数。这些参数会传给 `castUsing` 方法：

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
#### 可转换类与匿名转换类

结合使用可转换类与 PHP 的[匿名类](https://www.php.net/manual/en/language.oop5.anonymous.php)，可以将值对象及其转换逻辑定义在同一个可转换对象中。为此，从值对象的 `castUsing` 方法返回一个实现 `CastsAttributes` 接口的匿名类：

```php
<?php

namespace App\ValueObjects;

use Illuminate\Contracts\Database\Eloquent\Castable;
use Illuminate\Contracts\Database\Eloquent\CastsAttributes;

class Address implements Castable
{
    // ...

    /**
     * 获取用于在底层值与此转换目标之间进行转换的类。
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
