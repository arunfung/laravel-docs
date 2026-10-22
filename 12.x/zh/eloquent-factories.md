
# Eloquent: 数据工厂

-   [介绍](#introduction)
-   [定义模型工厂](#defining-model-factories)
    -   [生成工厂](#generating-factories)
    -   [工厂状态](#factory-states)
    -   [工厂回调](#factory-callbacks)
-   [使用工厂创建模型](#creating-models-using-factories)
    -   [实例化模型](#instantiating-models)
    -   [持久化模型](#persisting-models)
    -   [序列](#sequences)
-   [工厂关系](#factory-relationships)
    -   [一对多关系](#has-many-relationships)
    -   [属于关系](#belongs-to-relationships)
    -   [多对多关系](#many-to-many-relationships)
    -   [多态关系](#polymorphic-relationships)
    -   [在工厂中定义关系](#defining-relationships-within-factories)
    -   [复用已有模型来建立关系](#recycling-an-existing-model-for-relationships)

当测试你的应用程序或填充数据库时，你可能需要往数据库插入一些记录。
与其手动为每个列指定值，Laravel 允许你为每个 [Eloquent 模型](/docs/laravel/12.x/eloquent) 定义一组默认属性，这就是**模型工厂**。

要查看工厂的写法示例，可以看看应用中 `database/factories/UserFactory.php` 文件。
这个工厂在所有新的 Laravel 应用中都会包含，并且包含以下工厂定义：

```php
namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\User>
 */
class UserFactory extends Factory
{
    /**
     * 工厂当前使用的密码。
     */
    protected static ?string $password;

    /**
     * 定义模型的默认状态。
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'name' => fake()->name(),
            'email' => fake()->unique()->safeEmail(),
            'email_verified_at' => now(),
            'password' => static::$password ??= Hash::make('password'),
            'remember_token' => Str::random(10),
        ];
    }

    /**
     * 指定模型的邮箱地址应为未验证状态。
     */
    public function unverified(): static
    {
        return $this->state(fn (array $attributes) => [
            'email_verified_at' => null,
        ]);
    }
}
```



正如你所见，在最基本的形式下，工厂就是一些继承了 Laravel 基础工厂类的类，并定义了一个 `definition` 方法。
`definition` 方法返回一组默认的属性值，这些值会在使用工厂创建模型时被应用。

通过 `fake` 辅助函数，工厂可以访问 Faker PHP 库，这让你可以方便地生成各种用于测试和填充数据库的随机数据。

> [!注意]
> 你可以通过更新 `config/app.php` 配置文件中的 `faker_locale` 选项来更改应用程序的 Faker 语言环境。

## 定义模型工厂

### 生成工厂

要创建一个工厂，可以执行 `make:factory` [Artisan 命令](/docs/laravel/12.x/artisan)：

```shell
php artisan make:factory PostFactory
```

新的工厂类会被放置在 `database/factories` 目录中。

#### 模型与工厂的发现约定

一旦定义了工厂，你就可以通过 `Illuminate\Database\Eloquent\Factories\HasFactory` trait 为模型提供的静态 `factory` 方法来实例化该模型的工厂实例。

`HasFactory` trait 的 `factory` 方法会遵循一些约定来确定对应模型的工厂：

-   它会在 `Database\Factories` 命名空间下查找工厂；

-   工厂类的名字必须与模型名相同，并且以 `Factory` 结尾。

如果这些约定不适用于你的应用程序或工厂，你可以在模型上重写 `newFactory` 方法，直接返回该模型对应工厂的实例：

```php
use Database\Factories\Administration\FlightFactory;

/**
 * 为模型创建一个新的工厂实例。
 */
protected static function newFactory()
{
    return FlightFactory::new();
}
```



然后，在对应的工厂中定义一个 `model` 属性：

```php
use App\Administration\Flight;
use Illuminate\Database\Eloquent\Factories\Factory;

class FlightFactory extends Factory
{
    /**
     * 工厂所对应模型的类名。
     *
     * @var class-string<\Illuminate\Database\Eloquent\Model>
     */
    protected $model = Flight::class;
}
```

### 工厂状态（Factory States）

状态操作方法允许你定义一些离散的修改，这些修改可以以任意组合的形式应用到你的模型工厂上。
例如，你的 `Database\Factories\UserFactory` 工厂可能包含一个 `suspended` 状态方法，用来修改某个默认的属性值。

状态变换方法通常会调用 Laravel 基础工厂类提供的 `state` 方法。
`state` 方法接收一个闭包，该闭包会收到工厂定义的原始属性数组，并且需要返回一个用于修改的属性数组：

```php
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * 表示用户已被停用。
 */
public function suspended(): Factory
{
    return $this->state(function (array $attributes) {
        return [
            'account_status' => 'suspended',
        ];
    });
}
```

#### “Trashed” 状态

如果你的 Eloquent 模型支持 [软删除](/docs/laravel/12.x/eloquent#soft-deleting)，
你可以调用内置的 `trashed` 状态方法，来表示创建出来的模型应当已经被“软删除”。
你无需手动定义 `trashed` 状态，因为它在所有工厂中都是自动可用的：

```php
use App\Models\User;

$user = User::factory()->trashed()->create();
```

### 工厂回调（Factory Callbacks）

工厂回调是通过 `afterMaking` 和 `afterCreating` 方法注册的，允许你在生成或创建模型之后执行额外的任务。
你应该在工厂类中定义一个 `configure` 方法来注册这些回调。
当工厂实例化时，Laravel 会自动调用该方法：

```php
namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class UserFactory extends Factory
{
    /**
     * 配置模型工厂。
     */
    public function configure(): static
    {
        return $this->afterMaking(function (User $user) {
            // ...
        })->afterCreating(function (User $user) {
            // ...
        });
    }

    // ...
}
```



你也可以在状态方法中注册工厂回调，以执行特定于某个状态的额外任务：

```php
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * 表示用户已被停用。
 */
public function suspended(): Factory
{
    return $this->state(function (array $attributes) {
        return [
            'account_status' => 'suspended',
        ];
    })->afterMaking(function (User $user) {
        // ...
    })->afterCreating(function (User $user) {
        // ...
    });
}
```

## 使用工厂创建模型

### 实例化模型

一旦你定义了工厂，就可以使用 `Illuminate\Database\Eloquent\Factories\HasFactory` trait 为模型提供的静态 `factory` 方法，来实例化该模型的工厂实例。
我们来看看几个创建模型的示例。
首先，我们使用 `make` 方法来创建模型，但不将其持久化到数据库中：

```php
use App\Models\User;

$user = User::factory()->make();
```

你可以使用 `count` 方法一次性创建多个模型：

```php
$users = User::factory()->count(3)->make();
```

#### 应用状态

你也可以将任意的 [状态](#factory-states) 应用于模型。
如果你希望对模型应用多个状态变换，只需直接链式调用状态方法即可：

```php
$users = User::factory()->count(5)->suspended()->make();
```

#### 覆盖属性

如果你想覆盖模型的一些默认值，可以将一个数组传递给 `make` 方法。
只有指定的属性会被替换，其余的属性仍然会保留工厂中定义的默认值：

```php
$user = User::factory()->make([
    'name' => 'Abigail Otwell',
]);
```



或者，你也可以直接在工厂实例上调用 `state` 方法来执行内联状态变换：

```php
$user = User::factory()->state([
    'name' => 'Abigail Otwell',
])->make();
```

> [!注意]
> 当使用工厂创建模型时，[批量赋值保护](/docs/laravel/12.x/eloquent#mass-assignment) 会被自动禁用。

### 持久化模型

`create` 方法会实例化模型实例，并通过 Eloquent 的 `save` 方法将其持久化到数据库：

```php
use App\Models\User;

// 创建一个单独的 App\Models\User 实例...
$user = User::factory()->create();

// 创建三个 App\Models\User 实例...
$users = User::factory()->count(3)->create();
```

你也可以通过给 `create` 方法传递一个属性数组，来覆盖工厂的默认模型属性：

```php
$user = User::factory()->create([
    'name' => 'Abigail',
]);
```

### 序列（Sequences）

有时你可能希望在每次创建模型时交替更换某个模型属性的值。
你可以通过将状态变换定义为一个序列来实现。
例如，你可能希望在每个用户创建时交替设置 `admin` 字段的值为 `Y` 和 `N`：

```php
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Sequence;

$users = User::factory()
    ->count(10)
    ->state(new Sequence(
        ['admin' => 'Y'],
        ['admin' => 'N'],
    ))
    ->create();
```

在这个示例中，将会创建五个 `admin` 值为 `Y` 的用户，以及五个 `admin` 值为 `N` 的用户。

如果有需要，你还可以在序列值中包含闭包。每次序列需要新值时，该闭包都会被调用：

```php
use Illuminate\Database\Eloquent\Factories\Sequence;

$users = User::factory()
    ->count(10)
    ->state(new Sequence(
        fn (Sequence $sequence) => ['role' => UserRoles::all()->random()],
    ))
    ->create();
```



在序列闭包中，你可以访问传入闭包的序列实例上的 `$index` 或 `$count` 属性。
其中 `$index` 属性表示当前已经执行到序列的第几次迭代，而 `$count` 属性则表示序列将被调用的总次数：

```php
$users = User::factory()
    ->count(10)
    ->sequence(fn (Sequence $sequence) => ['name' => 'Name '.$sequence->index])
    ->create();
```

为了方便，序列也可以通过 `sequence` 方法来应用，它在内部实际上就是调用了 `state` 方法。
`sequence` 方法可以接收一个闭包或者一组属性数组：

```php
$users = User::factory()
    ->count(2)
    ->sequence(
        ['name' => 'First User'],
        ['name' => 'Second User'],
    )
    ->create();
```

## 工厂关系

### 一对多关系

接下来，让我们来探索如何通过 Laravel 提供的流畅工厂方法来构建 Eloquent 模型之间的关系。
首先，假设我们的应用中有一个 `App\Models\User` 模型和一个 `App\Models\Post` 模型。
同时假设 `User` 模型定义了一个与 `Post` 模型的一对多（hasMany）关系。

我们可以使用 Laravel 工厂提供的 `has` 方法来创建一个带有三个 `posts` 的用户。
`has` 方法接收一个工厂实例作为参数：

```php
use App\Models\Post;
use App\Models\User;

$user = User::factory()
    ->has(Post::factory()->count(3))
    ->create();
```

按照惯例，当你将 `Post` 模型传递给 `has` 方法时，Laravel 会假设 `User` 模型中存在一个名为 `posts` 的方法用于定义该关系。

如果有需要，你也可以显式地指定你想要操作的关系名称：

```php
$user = User::factory()
    ->has(Post::factory()->count(3), 'posts')
    ->create();
```



当然，你也可以对关联的模型执行状态操作。
此外，如果你的状态变更需要访问父模型，你也可以传递一个基于闭包的状态转换：

```php
$user = User::factory()
    ->has(
        Post::factory()
            ->count(3)
            ->state(function (array $attributes, User $user) {
                return ['user_type' => $user->type];
            })
        )
    ->create();
```

#### 使用魔术方法（Using Magic Methods）

为了方便，你可以使用 Laravel 的工厂魔术关系方法来构建关联关系。
例如，下面的示例会通过约定来确定相关模型应通过 `User` 模型上的 `posts` 关系方法来创建：

```php
$user = User::factory()
    ->hasPosts(3)
    ->create();
```

在使用魔术方法创建工厂关系时，你可以传递一个属性数组，用于覆盖关联模型上的属性：

```php
$user = User::factory()
    ->hasPosts(3, [
        'published' => false,
    ])
    ->create();
```

如果你的状态变更需要访问父模型，你也可以提供一个基于闭包的状态转换：

```php
$user = User::factory()
    ->hasPosts(3, function (array $attributes, User $user) {
        return ['user_type' => $user->type];
    })
    ->create();
```

### Belongs To 关系（Belongs To Relationships）

现在我们已经探索了如何使用工厂来构建“一对多”关系，接下来让我们探索这种关系的反向用法。
`for` 方法可用于定义工厂所创建的模型所隶属的父模型。
例如，我们可以创建三个属于同一个用户的 `App\Models\Post` 模型实例：

```php
use App\Models\Post;
use App\Models\User;

$posts = Post::factory()
    ->count(3)
    ->for(User::factory()->state([
        'name' => 'Jessica Archer',
    ]))
    ->create();
```



如果你已经有一个父模型实例，并且希望它与正在创建的模型关联起来，你可以将该模型实例传递给 `for` 方法：

```php
$user = User::factory()->create();

$posts = Post::factory()
    ->count(3)
    ->for($user)
    ->create();
```

#### 使用魔术方法

为了方便，你可以使用 Laravel 的工厂魔术关系方法来定义 “belongs to” 关系。
例如，下面的示例会通过约定来确定这三个 post 应该属于 `Post` 模型上的 `user` 关系：

```php
$posts = Post::factory()
    ->count(3)
    ->forUser([
        'name' => 'Jessica Archer',
    ])
    ->create();
```

### 多对多关系

和 [一对多关系](#has-many-relationships) 类似，“多对多”关系可以使用 `has` 方法来创建：

```php
use App\Models\Role;
use App\Models\User;

$user = User::factory()
    ->has(Role::factory()->count(3))
    ->create();
```

#### 中间表属性

如果你需要定义在连接模型的中间表 / 关联表上应设置的属性，可以使用 `hasAttached` 方法。
此方法的第二个参数接受一个包含中间表属性名和属性值的数组：

```php
use App\Models\Role;
use App\Models\User;

$user = User::factory()
    ->hasAttached(
        Role::factory()->count(3),
        ['active' => true]
    )
    ->create();
```

如果你的状态变更需要访问关联模型，你也可以提供一个基于闭包的状态转换：

```php
$user = User::factory()
    ->hasAttached(
        Role::factory()
            ->count(3)
            ->state(function (array $attributes, User $user) {
                return ['name' => $user->name.' Role'];
            }),
        ['active' => true]
    )
    ->create();
```



如果你已经有一些模型实例，并且希望它们被附加到你正在创建的模型上，你可以将这些模型实例传递给 `hasAttached` 方法。
在下面的示例中，相同的三个角色将会被附加到所有三个用户上：

```php
$roles = Role::factory()->count(3)->create();

$user = User::factory()
    ->count(3)
    ->hasAttached($roles, ['active' => true])
    ->create();
```

#### 使用魔术方法

为了方便，你可以使用 Laravel 的工厂魔术关系方法来定义多对多关系。
例如，下面的示例会通过约定来确定相关模型应当通过 `User` 模型上的 `roles` 关系方法来创建：

```php
$user = User::factory()
    ->hasRoles(1, [
        'name' => 'Editor'
    ])
    ->create();
```

### 多态关系

[多态关系](/docs/laravel/12.x/eloquent-relationships#polymorphic-relationships) 也可以通过工厂来创建。
多态的 “morph many” 关系的创建方式和典型的 “has many” 关系相同。
例如，如果 `App\Models\Post` 模型和 `App\Models\Comment` 模型之间存在一个 `morphMany` 关系：

```php
use App\Models\Post;

$post = Post::factory()->hasComments(3)->create();
```

#### Morph To 关系

魔术方法不能用于创建 `morphTo` 关系。
取而代之，必须直接使用 `for` 方法，并显式提供关系的名称。

例如，假设 `Comment` 模型有一个定义了 `morphTo` 关系的 `commentable` 方法。
在这种情况下，我们可以使用 `for` 方法直接创建三个属于同一篇 post 的评论：

```php
$comments = Comment::factory()->count(3)->for(
    Post::factory(), 'commentable'
)->create();
```



#### 多态多对多关系

多态的 “多对多” (`morphToMany` / `morphedByMany`) 关系的创建方式与非多态的 “多对多” 关系完全相同：

```php
use App\Models\Tag;
use App\Models\Video;

$videos = Video::factory()
    ->hasAttached(
        Tag::factory()->count(3),
        ['public' => true]
    )
    ->create();
```

当然，你也可以使用魔术的 `has` 方法来创建多态的 “多对多” 关系：

```php
$videos = Video::factory()
    ->hasTags(3, ['public' => true])
    ->create();
```

### 在工厂中定义关系

在模型工厂中定义关系时，通常会把一个新的工厂实例分配给关系的外键。
这种情况通常用于 “反向” 关系，比如 `belongsTo` 和 `morphTo` 关系。

例如，如果你希望在创建一篇文章时，同时创建一个新用户，可以这样写：

```php
use App\Models\User;

/**
 * 定义模型的默认状态。
 *
 * @return array<string, mixed>
 */
public function definition(): array
{
    return [
        'user_id' => User::factory(),
        'title' => fake()->title(),
        'content' => fake()->paragraph(),
    ];
}
```

如果关系的列依赖于定义它的工厂，你可以为属性分配一个闭包（closure）。
该闭包会接收工厂计算出的属性数组：

```php
/**
 * 定义模型的默认状态。
 *
 * @return array<string, mixed>
 */
public function definition(): array
{
    return [
        'user_id' => User::factory(),
        'user_type' => function (array $attributes) {
            return User::find($attributes['user_id'])->type;
        },
        'title' => fake()->title(),
        'content' => fake()->paragraph(),
    ];
}
```

### 在关系中复用已存在的模型

如果你有多个模型共享与另一个模型的同一个关系，可以使用 `recycle` 方法来确保在工厂创建的所有关系中复用同一个已存在的相关模型。




举例来说，假设你有 `Airline` 、 `Flight` 和 `Ticket` 模型，其中机票属于一家航空公司和一个航班，而航班也隶属于一家航空公司。在创建机票时，你可能希望为机票和航班选择相同的航空公司，因此可以将一家航空公司实例传递给 `recycle` 方法：

```php
Ticket::factory()
    ->recycle(Airline::factory()->create())
    ->create();
```

如果你的模型属于公共用户或团队，你可能会发现 `recycle` 方法特别有用。

`recycle` 方法还接受一组现有模型。当将一组模型提供给 `recycle` 方法时，工厂需要该类型的模型时会从集合中随机选择一个模型：

```php
Ticket::factory()
    ->recycle($airlines)
    ->create();
```
