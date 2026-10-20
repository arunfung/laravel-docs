# Eloquent：关联

- [简介](#introduction)
- [定义关联](#defining-relationships)
    - [一对一 / Has One](#one-to-one)
    - [一对多 / Has Many](#one-to-many)
    - [一对多（反向）/ Belongs To](#one-to-many-inverse)
    - [多记录中的单个关联](#has-one-of-many)
    - [远程一对一](#has-one-through)
    - [远程一对多](#has-many-through)
- [限定关联](#scoped-relationships)
- [多对多关联](#many-to-many)
    - [检索中间表列](#retrieving-intermediate-table-columns)
    - [通过中间表列筛选查询](#filtering-queries-via-intermediate-table-columns)
    - [通过中间表列排序查询](#ordering-queries-via-intermediate-table-columns)
    - [定义自定义中间表模型](#defining-custom-intermediate-table-models)
        - [自动填充中间模型的关联](#automatically-hydrating-pivot-relationships)
- [多态关联](#polymorphic-relationships)
    - [一对一](#one-to-one-polymorphic-relations)
    - [一对多](#one-to-many-polymorphic-relations)
    - [多记录中的单个关联](#one-of-many-polymorphic-relations)
    - [多对多](#many-to-many-polymorphic-relations)
    - [自定义多态类型](#custom-polymorphic-types)
- [动态关联](#dynamic-relationships)
- [查询关联](#querying-relations)
    - [关联方法与动态属性](#relationship-methods-vs-dynamic-properties)
    - [查询关联是否存在](#querying-relationship-existence)
    - [查询关联是否不存在](#querying-relationship-absence)
    - [查询 Morph To 关联](#querying-morph-to-relationships)
- [聚合关联模型](#aggregating-related-models)
    - [统计关联模型数量](#counting-related-models)
    - [其他聚合函数](#other-aggregate-functions)
    - [统计 Morph To 关联中的关联模型数量](#counting-related-models-on-morph-to-relationships)
- [预加载](#eager-loading)
    - [约束预加载](#constraining-eager-loads)
    - [延迟预加载](#lazy-eager-loading)
    - [自动预加载](#automatic-eager-loading)
    - [禁止延迟加载](#preventing-lazy-loading)
- [插入和更新关联模型](#inserting-and-updating-related-models)
    - [`save` 方法](#the-save-method)
    - [`create` 方法](#the-create-method)
    - [Belongs To 关联](#updating-belongs-to-relationships)
    - [多对多关联](#updating-many-to-many-relationships)
- [更新父模型时间戳](#touching-parent-timestamps)

<a name="introduction"></a>
## 简介

数据库表之间通常存在关联。例如，一篇博客文章可以有多条评论，一个订单也可以关联到下单的用户。Eloquent 让这些关联的管理和使用变得简单，并支持多种常见关联：

<div class="content-list" markdown="1">

- [一对一](#one-to-one)
- [一对多](#one-to-many)
- [多对多](#many-to-many)
- [远程一对一](#has-one-through)
- [远程一对多](#has-many-through)
- [一对一（多态）](#one-to-one-polymorphic-relations)
- [一对多（多态）](#one-to-many-polymorphic-relations)
- [多对多（多态）](#many-to-many-polymorphic-relations)

</div>

<a name="defining-relationships"></a>
## 定义关联

Eloquent 关联通过 Eloquent 模型类中的方法定义。关联本身也是强大的[查询构造器](/docs/{{version}}/queries)，因此将关联定义为方法，可以使用链式调用和查询功能。例如，可以在 `posts` 关联上继续添加查询约束：

```php
$user->posts()->where('active', 1)->get();
```

在深入使用关联之前，先来了解如何定义 Eloquent 支持的各种关联。

<a name="one-to-one"></a>
### 一对一 / Has One

一对一关联是最基本的数据库关联之一。例如，一个 `User` 模型可以关联一个 `Phone` 模型。要定义这种关联，可以在 `User` 模型中添加 `phone` 方法，调用 `hasOne` 并返回结果。模型通过 `Illuminate\Database\Eloquent\Model` 基类获得 `hasOne` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOne;

class User extends Model
{
    /**
     * 获取用户关联的手机。
     */
    public function phone(): HasOne
    {
        return $this->hasOne(Phone::class);
    }
}
```

`hasOne` 的第一个参数是关联模型的类名。定义关联后，就可以使用 Eloquent 的动态属性检索关联记录。动态属性让你能够像访问模型属性一样访问关联方法：

```php
$phone = User::find(1)->phone;
```

Eloquent 根据父模型的名称推断关联外键。在本例中，Eloquent 默认假定 `Phone` 模型具有 `user_id` 外键。要覆盖此约定，可以向 `hasOne` 传入第二个参数：

```php
return $this->hasOne(Phone::class, 'foreign_key');
```

此外，Eloquent 默认假定外键值与父模型的主键值匹配。换句话说，Eloquent 会用用户的 `id` 列值，查找 `Phone` 记录中 `user_id` 列的匹配值。如果希望使用 `id` 或模型主键以外的列作为关联的本地键，可以向 `hasOne` 传入第三个参数：

```php
return $this->hasOne(Phone::class, 'foreign_key', 'local_key');
```

<a name="one-to-one-defining-the-inverse-of-the-relationship"></a>
#### 定义反向关联

现在可以通过 `User` 模型访问 `Phone` 模型了。接下来，在 `Phone` 模型中定义一个关联，以便访问拥有该手机的用户。可以使用 `belongsTo` 定义 `hasOne` 的反向关联：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Phone extends Model
{
    /**
     * 获取拥有该手机的用户。
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
```

调用 `user` 方法时，Eloquent 会尝试查找 `id` 与 `Phone` 模型的 `user_id` 列值匹配的 `User` 模型。

Eloquent 会通过检查关联方法的名字，并在方法名后追加 `_id`，来推断外键的名称。所以在本例中，Eloquent 默认假设 `Phone` 模型中存在 `user_id` 列。但是，如果 `Phone` 模型中的外键并不是 `user_id`，你可以在 `belongsTo` 方法中传递第二个参数来自定义外键名称：

```php
/**
 * 获取拥有该手机的用户。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class, 'foreign_key');
}
```

如果父模型没有使用 `id` 作为主键，或者你希望通过其他列来查找关联模型，可以在 `belongsTo` 方法中传递第三个参数，用于指定父表的自定义键：

```php
/**
 * 获取拥有该手机的用户。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class, 'foreign_key', 'owner_key');
}
```

<a name="one-to-many"></a>
### 一对多 / Has Many

一对多关联用于表示一个父模型拥有一个或多个子模型。例如，一篇博客文章可以有任意多条评论。与其他 Eloquent 关联一样，一对多关联也是通过在 Eloquent 模型中定义方法来实现的：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Post extends Model
{
    /**
     * 获取博客文章的评论。
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }
}
```

Eloquent 会自动推断 `Comment` 模型的外键列。按照约定，它会将父模型名称转换为下划线命名法（snake case），再追加 `_id`。因此，本例中 `Comment` 模型的外键列为 `post_id`。

定义关联方法后，就可以通过 `comments` 属性访问关联评论的[集合](/docs/{{version}}/eloquent-collections)。Eloquent 提供了「动态关联属性」，因此可以像访问模型属性一样访问关联方法：

```php
use App\Models\Post;

$comments = Post::find(1)->comments;

foreach ($comments as $comment) {
    // ...
}
```

由于所有关联也同时作为查询构造器使用，你可以通过调用 `comments` 方法，并在查询上继续链式添加条件，从而为关联查询添加更多约束：

```php
$comment = Post::find(1)->comments()
    ->where('title', 'foo')
    ->first();
```

和 `hasOne` 方法类似，你也可以通过向 `hasMany` 方法传递额外参数来覆盖外键和本地键：

```php
return $this->hasMany(Comment::class, 'foreign_key');

return $this->hasMany(Comment::class, 'foreign_key', 'local_key');
```

<a name="automatically-hydrating-parent-models-on-children"></a>
#### 在子模型中自动填充父模型

即使使用了 Eloquent 预加载，如果在循环子模型时访问其父模型，也可能出现「N + 1」查询问题：

```php
$posts = Post::with('comments')->get();

foreach ($posts as $post) {
    foreach ($post->comments as $comment) {
        echo $comment->post->title;
    }
}
```

在上例中，虽然已经为每个 `Post` 模型预加载了评论，但 Eloquent 不会自动在每个子 `Comment` 模型中填充父 `Post` 模型，因此仍然产生了「N + 1」查询问题。

要让 Eloquent 自动在子模型中填充父模型，可以在定义 `hasMany` 关联时调用 `chaperone` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Post extends Model
{
    /**
     * 获取博客文章的评论。
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class)->chaperone();
    }
}
```

也可以在预加载关联时调用 `chaperone` 方法，在运行时启用父模型的自动填充：

```php
use App\Models\Post;

$posts = Post::with([
    'comments' => fn ($comments) => $comments->chaperone(),
])->get();
```

<a name="one-to-many-inverse"></a>
### 一对多（反向）/ Belongs To

现在可以访问文章的所有评论了，接下来定义一个关联，让评论也能访问所属文章。要定义 `hasMany` 的反向关联，可以在子模型中定义一个调用 `belongsTo` 的关联方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Comment extends Model
{
    /**
     * 获取评论所属的文章。
     */
    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }
}
```

定义好关联后，我们可以通过访问 `post` 「动态关联属性」来获取评论的父文章：

```php
use App\Models\Comment;

$comment = Comment::find(1);

return $comment->post->title;
```

在上例中，Eloquent 会尝试查找 `id` 与 `Comment` 模型的 `post_id` 列值匹配的 `Post` 模型。

Eloquent 根据关联方法的名称推断默认外键：在方法名后追加 `_` 和父模型的主键列名。因此，在本例中，Eloquent 默认假定 `comments` 表中指向 `Post` 模型的外键为 `post_id`。

但是，如果关联的外键不遵循这些约定，你可以在 `belongsTo` 方法中传递第二个参数，自定义外键名称：

```php
/**
 * 获取评论所属的文章。
 */
public function post(): BelongsTo
{
    return $this->belongsTo(Post::class, 'foreign_key');
}
```

如果父模型没有使用 `id` 作为主键，或者你希望通过其他列查找关联模型，可以在 `belongsTo` 方法中传递第三个参数，指定父表的自定义键：

```php
/**
 * 获取评论所属的文章。
 */
public function post(): BelongsTo
{
    return $this->belongsTo(Post::class, 'foreign_key', 'owner_key');
}
```

<a name="default-models"></a>
#### 默认模型

`belongsTo`、`hasOne`、`hasOneThrough` 和 `morphOne` 关联允许定义默认模型，在关联为 `null` 时返回。这通常称为[空对象模式](https://en.wikipedia.org/wiki/Null_Object_pattern)，有助于减少代码中的条件判断。在下面的示例中，如果 `Post` 模型没有关联用户，`user` 关联将返回一个空的 `App\Models\User` 模型：

```php
/**
 * 获取文章作者。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class)->withDefault();
}
```

如果希望在默认模型中填充属性，可以向 `withDefault` 方法传递一个数组或闭包：

```php
/**
 * 获取文章作者。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class)->withDefault([
        'name' => 'Guest Author',
    ]);
}

/**
 * 获取文章作者。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class)->withDefault(function (User $user, Post $post) {
        $user->name = 'Guest Author';
    });
}
```

<a name="querying-belongs-to-relationships"></a>
#### 查询 Belongs To 关联

在查询「belongs to」关联的子模型时，你可以手动构建 `where` 条件以获取对应的 Eloquent 模型：

```php
use App\Models\Post;

$posts = Post::where('user_id', $user->id)->get();
```

不过，你可能会发现使用 `whereBelongsTo` 方法更方便，它会自动判断给定模型的关联和外键：

```php
$posts = Post::whereBelongsTo($user)->get();
```

你还可以向 `whereBelongsTo` 方法传递一个 [集合](/docs/{{version}}/eloquent-collections) 实例。在这种情况下，Laravel 会获取属于集合中任意父模型的子模型：

```php
$users = User::where('vip', true)->get();

$posts = Post::whereBelongsTo($users)->get();
```

默认情况下，Laravel 根据给定模型的类名确定对应的关联。也可以将关联名称作为 `whereBelongsTo` 的第二个参数，手动指定关联：

```php
$posts = Post::whereBelongsTo($user, 'author')->get();
```

<a name="has-one-of-many"></a>
### 多记录中的单个关联

有时，一个模型可能关联多个相关模型，但你希望方便地获取该关联中「最新」或「最旧」的相关模型。例如，`User` 模型可能关联多个 `Order` 模型，但你希望定义一种便捷方式来操作用户最近下的订单。你可以使用 `hasOne` 关联类型结合 `ofMany` 方法来实现：

```php
/**
 * 获取用户最近的订单。
 */
public function latestOrder(): HasOne
{
    return $this->hasOne(Order::class)->latestOfMany();
}
```

同样，也可以定义一个方法，检索关联中「最早」的模型，即第一个关联模型：

```php
/**
 * 获取用户最早的订单。
 */
public function oldestOrder(): HasOne
{
    return $this->hasOne(Order::class)->oldestOfMany();
}
```

默认情况下，`latestOfMany` 和 `oldestOfMany` 方法会根据模型的主键来获取最新或最旧的相关模型，该主键必须是可排序的。但是，有时你可能希望根据其他排序条件，从更大的关联集合中获取单个模型。

例如，可以使用 `ofMany` 获取用户金额最高的订单。第一个参数是可排序的列，第二个参数是查询关联模型时使用的聚合函数（`min` 或 `max`）：

```php
/**
 * 获取用户金额最高的订单。
 */
public function largestOrder(): HasOne
{
    return $this->hasOne(Order::class)->ofMany('price', 'max');
}
```

> [!WARNING]
> 由于 PostgreSQL 不支持对 UUID 列执行 `MAX` 函数，目前无法将多记录中的单个关联与 PostgreSQL UUID 列结合使用。

<a name="converting-many-relationships-to-has-one-relationships"></a>
#### 将「多」关联转换为 Has One 关联

通常，当使用 `latestOfMany`、`oldestOfMany` 或 `ofMany` 方法获取单个模型时，你可能已经为同一模型定义了「has many」关联。为了方便，Laravel 允许你通过在关联上调用 `one` 方法，将该关联轻松转换为「has one」关联：

```php
/**
 * 获取用户的订单。
 */
public function orders(): HasMany
{
    return $this->hasMany(Order::class);
}

/**
 * 获取用户金额最高的订单。
 */
public function largestOrder(): HasOne
{
    return $this->orders()->one()->ofMany('price', 'max');
}
```

你也可以使用 `one` 方法将 `HasManyThrough` 关联转换为 `HasOneThrough` 关联：

```php
public function latestDeployment(): HasOneThrough
{
    return $this->deployments()->one()->latestOfMany();
}
```

<a name="advanced-has-one-of-many-relationships"></a>
#### 高级多记录中的单个关联

有时可能需要构建更高级的「has one of many」关联。例如，`Product` 模型可能关联多个 `Price` 模型，即使在发布新价格后，这些价格仍会保留在系统中。此外，该产品的新价格数据可能会提前发布，通过 `published_at` 列在未来某个时间生效。

因此，我们需要检索生效时间不在未来的最新价格。如果两条价格的生效时间相同，则优先选择 ID 较大的价格。为此，需要向 `ofMany` 传入一个数组，指定用于确定最新价格的排序列；再传入一个闭包作为第二个参数，为关联查询添加额外的生效时间约束：

```php
/**
 * 获取产品当前的价格。
 */
public function currentPricing(): HasOne
{
    return $this->hasOne(Price::class)->ofMany([
        'published_at' => 'max',
        'id' => 'max',
    ], function (Builder $query) {
        $query->where('published_at', '<', now());
    });
}
```

<a name="has-one-through"></a>
### 远程一对一

「远程一对一」关联定义了与另一个模型的一对一关联，表示当前模型可以 _通过_ 第三个模型关联到另一个模型的单个实例。

例如，在一个汽车修理厂应用中，每个 `Mechanic` 模型可能关联一个 `Car` 模型，而每个 `Car` 模型又可能关联一个 `Owner` 模型。虽然技师和车主在数据库中没有直接关联，但技师可以通过 `Car` 模型访问车主。让我们先来看一下定义这种关联所需的数据表：

```text
mechanics
    id - integer
    name - string

cars
    id - integer
    model - string
    mechanic_id - integer

owners
    id - integer
    name - string
    car_id - integer
```

现在我们已经了解了这种关联的数据表结构，接下来在 `Mechanic` 模型中定义关联：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

class Mechanic extends Model
{
    /**
     * 获取车主。
     */
    public function carOwner(): HasOneThrough
    {
        return $this->hasOneThrough(Owner::class, Car::class);
    }
}
```

传递给 `hasOneThrough` 方法的第一个参数是我们希望访问的最终模型名称，第二个参数是中间模型的名称。

或者，如果在关联涉及的所有模型上都已经定义了相应的关联，你也可以通过调用 `through` 方法并提供这些关联的名称，来更简洁地定义「has-one-through」关联。例如，如果 `Mechanic` 模型有一个 `cars` 关联，而 `Car` 模型有一个 `owner` 关联，那么就可以这样定义一个连接技师和车主的「has-one-through」关联：

```php
// 基于字符串的语法……
return $this->through('cars')->has('owner');

// 动态语法……
return $this->throughCars()->hasOwner();
```

<a name="has-one-through-key-conventions"></a>
#### 键的约定

在执行关联查询时，将使用典型的 Eloquent 外键约定。如果你想自定义关联的键，可以将它们作为第三个和第四个参数传递给 `hasOneThrough` 方法。第三个参数是中间模型上的外键名称，第四个参数是最终模型上的外键名称。第五个参数是本地键，而第六个参数是中间模型的本地键：

```php
class Mechanic extends Model
{
    /**
     * 获取车主。
     */
    public function carOwner(): HasOneThrough
    {
        return $this->hasOneThrough(
            Owner::class,
            Car::class,
            'mechanic_id', // cars 表的外键……
            'car_id', // owners 表的外键……
            'id', // mechanics 表的本地键……
            'id' // cars 表的本地键……
        );
    }
}
```

如前所述，如果涉及的所有模型都已定义相应关联，也可以调用 `through` 并传入关联名称，以链式语法定义「远程一对一」关联。这样可以复用现有关联中的键约定：

```php
// 基于字符串的语法……
return $this->through('cars')->has('owner');

// 动态语法……
return $this->throughCars()->hasOwner();
```

<a name="has-many-through"></a>
### 远程一对多

「远程一对多」关联允许通过中间关联便捷地访问远端关联。例如，假设正在构建类似 [Laravel Cloud](https://cloud.laravel.com) 的部署平台，`Application` 模型可以通过中间的 `Environment` 模型访问多个 `Deployment` 模型，从而获取指定应用的所有部署。定义该关联所需的表结构如下：

```text
applications
    id - integer
    name - string

environments
    id - integer
    application_id - integer
    name - string

deployments
    id - integer
    environment_id - integer
    commit_hash - string
```

现在我们已经了解了定义这种关联所需的表结构，接下来在 `Application` 模型中定义关联：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasManyThrough;

class Application extends Model
{
    /**
     * 获取应用的所有部署。
     */
    public function deployments(): HasManyThrough
    {
        return $this->hasManyThrough(Deployment::class, Environment::class);
    }
}
```

传递给 `hasManyThrough` 方法的第一个参数是我们希望访问的最终模型名称，第二个参数是中间模型的名称。

如果涉及的所有模型都已定义相应关联，也可以调用 `through` 并传入关联名称，以链式语法定义「远程一对多」关联。例如，如果 `Application` 模型有 `environments` 关联，而 `Environment` 模型有 `deployments` 关联，就可以这样连接应用与部署：

```php
// 基于字符串的语法……
return $this->through('environments')->has('deployments');

// 动态语法……
return $this->throughEnvironments()->hasDeployments();
```

虽然 `Deployment` 模型对应的表没有 `application_id` 列，但通过 `hasManyThrough` 关联，仍然可以使用 `$application->deployments` 访问应用的部署。Eloquent 会检查中间模型 `Environment` 对应表中的 `application_id` 列，找到相关环境的 ID，再用这些 ID 查询 `Deployment` 模型对应的表。

<a name="has-many-through-key-conventions"></a>
#### 键的约定

在执行关联查询时，将使用典型的 Eloquent 外键约定。如果你想自定义关联的键，可以将它们作为第三个和第四个参数传递给 `hasManyThrough` 方法。第三个参数是中间模型上的外键名称，第四个参数是最终模型上的外键名称。第五个参数是本地键，第六个参数是中间模型的本地键：

```php
class Application extends Model
{
    public function deployments(): HasManyThrough
    {
        return $this->hasManyThrough(
            Deployment::class,
            Environment::class,
            'application_id', // environments 表的外键……
            'environment_id', // deployments 表的外键……
            'id', // applications 表的本地键……
            'id' // environments 表的本地键……
        );
    }
}
```

如前所述，如果涉及的所有模型都已定义相应关联，也可以调用 `through` 并传入关联名称，以链式语法定义「远程一对多」关联。这样可以复用现有关联中的键约定：

```php
// 基于字符串的语法……
return $this->through('environments')->has('deployments');

// 动态语法……
return $this->throughEnvironments()->hasDeployments();
```

<a name="scoped-relationships"></a>
### 限定关联

我们经常会在模型中添加额外方法，为关联设置约束。例如，可以在 `User` 模型中添加 `featuredPosts` 方法，在原有 `posts` 关联上追加 `where` 条件：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    /**
     * 获取用户的文章。
     */
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class)->latest();
    }

    /**
     * 获取用户的精选文章。
     */
    public function featuredPosts(): HasMany
    {
        return $this->posts()->where('featured', true);
    }
}
```

但是，如果你尝试通过 `featuredPosts` 方法创建模型，它的 `featured` 属性不会被设置为 `true`。如果你希望通过关联方法创建模型时，同时为所有通过该关联创建的模型指定默认属性，可以在构建关联查询时使用 `withAttributes` 方法：

```php
/**
 * 获取用户的精选文章。
 */
public function featuredPosts(): HasMany
{
    return $this->posts()->withAttributes(['featured' => true]);
}
```

`withAttributes` 方法会使用给定属性向查询添加 `where` 条件，并将这些属性添加到通过关联方法创建的任何模型上：

```php
$post = $user->featuredPosts()->create(['title' => 'Featured Post']);

$post->featured; // true
```

要指示 `withAttributes` 方法不要向查询添加 `where` 条件，可以将 `asConditions` 参数设置为 `false`：

```php
return $this->posts()->withAttributes(['featured' => true], asConditions: false);
```

<a name="many-to-many"></a>
## 多对多关联

多对多关联比 `hasOne` 和 `hasMany` 关联稍微复杂一些。例如，一个用户可以有多个角色，而这些角色也可以由其他用户共享。一个用户可以同时拥有「作者」和「编辑」角色，其他用户也可以拥有这些角色。因此，一个用户有多个角色，一个角色也有多个用户。

<a name="many-to-many-table-structure"></a>
#### 表结构

要定义这种关联，需要三个数据库表：`users`、`roles` 和 `role_user`。`role_user` 表的名称来源于相关模型名称的字母顺序，并包含 `user_id` 和 `role_id` 列。该表用作连接用户和角色的中间表。

由于一个角色可以属于多个用户，不能直接在 `roles` 表中添加 `user_id` 列，否则一个角色就只能属于一个用户。要支持将角色分配给多个用户，需要使用 `role_user` 表。关联的表结构如下：

```text
users
    id - integer
    name - string

roles
    id - integer
    name - string

role_user
    user_id - integer
    role_id - integer
```

<a name="many-to-many-model-structure"></a>
#### 模型结构

多对多关联通过定义一个返回 `belongsToMany` 结果的方法来实现。`belongsToMany` 由所有 Eloquent 模型继承的 `Illuminate\Database\Eloquent\Model` 基类提供。例如，在 `User` 模型中定义 `roles` 方法，并将关联模型的类名作为 `belongsToMany` 的第一个参数：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class User extends Model
{
    /**
     * 用户拥有的角色。
     */
    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class);
    }
}
```

定义关联后，你可以使用 `roles` 动态关联属性访问用户的角色：

```php
use App\Models\User;

$user = User::find(1);

foreach ($user->roles as $role) {
    // ...
}
```

由于所有关联也可用作查询构造器，你可以通过调用 `roles` 方法并继续在查询上链式添加条件，为关联查询添加更多约束：

```php
$roles = User::find(1)->roles()->orderBy('name')->get();
```

要确定关联中间表的表名，Eloquent 会按字母顺序连接两个相关模型的名称。但是，你可以自由覆盖此约定。可以通过向 `belongsToMany` 方法传递第二个参数来实现：

```php
return $this->belongsToMany(Role::class, 'role_user');
```

除了自定义中间表名称外，你还可以通过向 `belongsToMany` 方法传递额外参数自定义表中键的列名。第三个参数是你正在定义关联的模型的外键名称，而第四个参数是你要关联的模型的外键名称：

```php
return $this->belongsToMany(Role::class, 'role_user', 'user_id', 'role_id');
```

<a name="many-to-many-defining-the-inverse-of-the-relationship"></a>
#### 定义反向关联

要定义多对多关联的「反向关联」，应在关联模型中定义一个同样返回 `belongsToMany` 结果的方法。继续用户与角色的示例，在 `Role` 模型中定义 `users` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Role extends Model
{
    /**
     * 拥有该角色的用户。
     */
    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class);
    }
}
```

如你所见，该关联的定义与 `User` 模型的对应关联完全相同，只是引用了 `App\Models\User` 模型。由于我们复用了 `belongsToMany` 方法，在定义多对多关联的「反向关联」时，所有常用的表名和键自定义选项依然可用。

<a name="retrieving-intermediate-table-columns"></a>
### 检索中间表列

如你所学，使用多对多关联需要存在中间表。Eloquent 提供了一些非常方便的方法与该表交互。例如，假设我们的 `User` 模型关联了多个 `Role` 模型。访问该关联后，可以通过模型上的 `pivot` 属性访问中间表：

```php
use App\Models\User;

$user = User::find(1);

foreach ($user->roles as $role) {
    echo $role->pivot->created_at;
}
```

注意，每个我们获取的 `Role` 模型都会自动分配一个 `pivot` 属性。该属性包含一个表示中间表的模型。

默认情况下，`pivot` 模型上只会包含模型的键。如果你的中间表包含额外的属性，则必须在定义关联时指定它们：

```php
return $this->belongsToMany(Role::class)->withPivot('active', 'created_by');
```

如果你希望中间表拥有由 Eloquent 自动维护的 `created_at` 和 `updated_at` 时间戳，可以在定义关联时调用 `withTimestamps` 方法：

```php
return $this->belongsToMany(Role::class)->withTimestamps();
```

> [!WARNING]
> 使用 Eloquent 自动维护时间戳的中间表，必须同时包含 `created_at` 和 `updated_at` 时间戳列。

<a name="customizing-the-pivot-attribute-name"></a>
#### 自定义 `pivot` 属性名称

如前所述，可以通过模型上的 `pivot` 属性访问中间表的属性。但是，你可以自定义该属性名称，以更好地反映它在应用中的用途。

例如，如果你的应用中包含可订阅播客的用户，很可能用户与播客之间存在多对多关联。在这种情况下，你可能希望将中间表属性重命名为 `subscription` 而不是 `pivot`。这可以在定义关联时使用 `as` 方法实现：

```php
return $this->belongsToMany(Podcast::class)
    ->as('subscription')
    ->withTimestamps();
```

一旦指定了自定义的中间表属性，就可以使用自定义名称访问中间表数据：

```php
$users = User::with('podcasts')->get();

foreach ($users->flatMap->podcasts as $podcast) {
    echo $podcast->subscription->created_at;
}
```

<a name="filtering-queries-via-intermediate-table-columns"></a>
### 通过中间表列筛选查询

定义关联时，可以使用 `wherePivot`、`wherePivotIn`、`wherePivotNotIn`、`wherePivotBetween`、`wherePivotNotBetween`、`wherePivotNull` 和 `wherePivotNotNull`，筛选 `belongsToMany` 关联查询返回的结果：

```php
return $this->belongsToMany(Role::class)
    ->wherePivot('approved', 1);

return $this->belongsToMany(Role::class)
    ->wherePivotIn('priority', [1, 2]);

return $this->belongsToMany(Role::class)
    ->wherePivotNotIn('priority', [1, 2]);

return $this->belongsToMany(Podcast::class)
    ->as('subscriptions')
    ->wherePivotBetween('created_at', ['2020-01-01 00:00:00', '2020-12-31 00:00:00']);

return $this->belongsToMany(Podcast::class)
    ->as('subscriptions')
    ->wherePivotNotBetween('created_at', ['2020-01-01 00:00:00', '2020-12-31 00:00:00']);

return $this->belongsToMany(Podcast::class)
    ->as('subscriptions')
    ->wherePivotNull('expired_at');

return $this->belongsToMany(Podcast::class)
    ->as('subscriptions')
    ->wherePivotNotNull('expired_at');
```

`wherePivot` 会向查询添加一个 where 条件约束，但在通过定义的关联创建新模型时不会添加指定的值。如果你需要在查询和创建关联时都使用特定的 pivot 值，可以使用 `withPivotValue` 方法：

```php
return $this->belongsToMany(Role::class)
    ->withPivotValue('approved', 1);
```

<a name="ordering-queries-via-intermediate-table-columns"></a>
### 通过中间表列排序查询

可以使用 `orderByPivot` 和 `orderByPivotDesc`，对 `belongsToMany` 关联查询返回的结果排序。下面的示例将检索用户的徽章，并按创建时间从新到旧排序：

```php
return $this->belongsToMany(Badge::class)
    ->where('rank', 'gold')
    ->orderByPivotDesc('created_at');
```

<a name="defining-custom-intermediate-table-models"></a>
### 定义自定义中间表模型

要为多对多关联的中间表定义自定义模型，可以在定义关联时调用 `using`。自定义中间模型允许添加方法、类型转换等额外行为。

自定义多对多中间模型应继承 `Illuminate\Database\Eloquent\Relations\Pivot`，自定义多态多对多中间模型则应继承 `Illuminate\Database\Eloquent\Relations\MorphPivot`。例如，下面定义了使用自定义中间模型 `RoleUser` 的 `Role` 模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Role extends Model
{
    /**
     * 拥有该角色的用户。
     */
    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class)->using(RoleUser::class);
    }
}
```

在定义 `RoleUser` 模型时，应继承 `Illuminate\Database\Eloquent\Relations\Pivot` 类：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;

class RoleUser extends Pivot
{
    // ...
}
```

> [!WARNING]
> 中间模型不能使用 `SoftDeletes` trait。如果需要软删除中间表记录，请考虑将中间模型转换为普通 Eloquent 模型。

<a name="custom-pivot-models-and-incrementing-ids"></a>
#### 自定义中间模型与自增 ID

如果多对多关联使用自定义中间模型，且该模型的主键是自增的，应确保在自定义中间模型上使用 `Table` 特性，并将 `incrementing` 设为 `true`：

```php
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Relations\Pivot;

#[Table(incrementing: true)]
class RoleUser extends Pivot
{
    // ...
}
```

<a name="automatically-hydrating-pivot-relationships"></a>
#### 自动填充中间模型的关联

如果自定义中间模型为定义关联的一方和关联的另一方都定义了 `belongsTo` 关联，可以调用 `chaperone`，自动在每个中间模型中填充这些关联，从而避免通过中间模型访问两端模型时执行额外查询：

```php
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\Pivot;

class RoleUser extends Pivot
{
    public function role(): BelongsTo
    {
        return $this->belongsTo(Role::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}

class Role extends Model
{
    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class)
            ->using(RoleUser::class)
            ->chaperone();
    }
}
```

Eloquent 会尝试推断中间模型的关联名称。如果中间模型使用了非标准名称，可以向 `chaperone` 传入定义关联的一方和关联的另一方所对应的关联名称：

```php
return $this->belongsToMany(User::class)
    ->using(RoleUser::class)
    ->chaperone(declaring: 'role', related: 'user');
```

<a name="polymorphic-relationships"></a>
## 多态关联

多态关联允许子模型通过同一个关联归属于多种类型的模型。例如，在允许用户分享博客文章和视频的应用中，`Comment` 模型既可以属于 `Post` 模型，也可以属于 `Video` 模型。

<a name="one-to-one-polymorphic-relations"></a>
### 一对一（多态）

<a name="one-to-one-polymorphic-table-structure"></a>
#### 表结构

一对一多态关联与普通的一对一关联类似，但子模型可以通过同一个关联归属于多种类型的模型。例如，博客文章 `Post` 和用户 `User` 都可以通过多态关联拥有 `Image` 模型。使用一对一多态关联，可以将图片统一存放在一张表中，每张图片都可以关联到文章或用户。先来看表结构：

```text
posts
    id - integer
    name - string

users
    id - integer
    name - string

images
    id - integer
    url - string
    imageable_type - string
    imageable_id - integer
```

注意 `images` 表中的 `imageable_id` 和 `imageable_type` 列。`imageable_id` 保存文章或用户的 ID，`imageable_type` 保存父模型的类名。访问 `imageable` 关联时，Eloquent 根据 `imageable_type` 判断应返回哪种类型的父模型。在本例中，该列的值为 `App\Models\Post` 或 `App\Models\User`。

<a name="one-to-one-polymorphic-model-structure"></a>
#### 模型结构

接下来，让我们查看构建此关联所需的模型定义：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class Image extends Model
{
    /**
     * 获取 imageable 父模型（用户或文章）。
     */
    public function imageable(): MorphTo
    {
        return $this->morphTo();
    }
}

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphOne;

class Post extends Model
{
    /**
     * 获取文章的图片。
     */
    public function image(): MorphOne
    {
        return $this->morphOne(Image::class, 'imageable');
    }
}

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphOne;

class User extends Model
{
    /**
     * 获取用户的图片。
     */
    public function image(): MorphOne
    {
        return $this->morphOne(Image::class, 'imageable');
    }
}
```

<a name="one-to-one-polymorphic-retrieving-the-relationship"></a>
#### 检索关联

定义数据库表和模型后，你可以通过模型访问这些关联。例如，要获取文章的图片，可以访问 `image` 动态关联属性：

```php
use App\Models\Post;

$post = Post::find(1);

$image = $post->image;
```

要检索多态模型的父模型，可以将调用 `morphTo` 的方法名作为动态关联属性访问。在本例中，就是访问 `Image` 模型的 `imageable`：

```php
use App\Models\Image;

$image = Image::find(1);

$imageable = $image->imageable;
```

`Image` 模型的 `imageable` 关联会根据图片所属的模型类型，返回 `Post` 或 `User` 实例。

<a name="morph-one-to-one-key-conventions"></a>
#### 键的约定

如有必要，你可以指定多态子模型使用的「id」和「type」列的名称。如果这样做，请确保始终将关联名称作为第一个参数传递给 `morphTo` 方法。通常，该值应与方法名匹配，因此你可以使用 PHP 的 `__FUNCTION__` 常量：

```php
/**
 * 获取图片所属的模型。
 */
public function imageable(): MorphTo
{
    return $this->morphTo(__FUNCTION__, 'imageable_type', 'imageable_id');
}
```

<a name="one-to-many-polymorphic-relations"></a>
### 一对多（多态）

<a name="one-to-many-polymorphic-table-structure"></a>
#### 表结构

一对多多态关联类似于典型的一对多关联；但是，子模型可以通过单一关联属于多种类型的模型。例如，假设你的应用用户可以对文章和视频进行“评论”。使用多态关联，你可以使用单个 `comments` 表存储文章和视频的评论。首先，让我们查看构建此关联所需的表结构：

```text
posts
    id - integer
    title - string
    body - text

videos
    id - integer
    title - string
    url - string

comments
    id - integer
    body - text
    commentable_type - string
    commentable_id - integer
```

<a name="one-to-many-polymorphic-model-structure"></a>
#### 模型结构

接下来，让我们查看构建此关联所需的模型定义：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class Comment extends Model
{
    /**
     * 获取 commentable 父模型（文章或视频）。
     */
    public function commentable(): MorphTo
    {
        return $this->morphTo();
    }
}

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class Post extends Model
{
    /**
     * 获取文章的所有评论。
     */
    public function comments(): MorphMany
    {
        return $this->morphMany(Comment::class, 'commentable');
    }
}

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class Video extends Model
{
    /**
     * 获取视频的所有评论。
     */
    public function comments(): MorphMany
    {
        return $this->morphMany(Comment::class, 'commentable');
    }
}
```

<a name="one-to-many-polymorphic-retrieving-the-relationship"></a>
#### 检索关联

定义数据库表和模型后，你可以通过模型的动态关联属性访问这些关联。例如，要访问文章的所有评论，可以使用 `comments` 动态属性：

```php
use App\Models\Post;

$post = Post::find(1);

foreach ($post->comments as $comment) {
    // ...
}
```

要检索多态子模型的父模型，也可以将调用 `morphTo` 的方法名作为动态关联属性访问。在本例中，就是通过 `Comment` 模型的 `commentable` 访问评论所属的父模型：

```php
use App\Models\Comment;

$comment = Comment::find(1);

$commentable = $comment->commentable;
```

`Comment` 模型的 `commentable` 关联会根据评论所属的父模型类型，返回 `Post` 或 `Video` 实例。

<a name="polymorphic-automatically-hydrating-parent-models-on-children"></a>
#### 在子模型中自动填充父模型

即使使用 Eloquent 预加载，如果在循环子模型时尝试访问子模型的父模型，也可能出现「N + 1」查询问题：

```php
$posts = Post::with('comments')->get();

foreach ($posts as $post) {
    foreach ($post->comments as $comment) {
        echo $comment->commentable->title;
    }
}
```

在上例中，虽然已经为每个 `Post` 模型预加载了评论，但 Eloquent 不会自动在每个子 `Comment` 模型中填充父 `Post` 模型，因此仍然产生了「N + 1」查询问题。

要让 Eloquent 自动在子模型中填充父模型，可以在定义 `morphMany` 关联时调用 `chaperone` 方法：

```php
class Post extends Model
{
    /**
     * 获取文章的所有评论。
     */
    public function comments(): MorphMany
    {
        return $this->morphMany(Comment::class, 'commentable')->chaperone();
    }
}
```

也可以在预加载关联时调用 `chaperone` 方法，在运行时启用父模型的自动填充：

```php
use App\Models\Post;

$posts = Post::with([
    'comments' => fn ($comments) => $comments->chaperone(),
])->get();
```

<a name="one-of-many-polymorphic-relations"></a>
### 多记录中的单个关联（多态）

有时，一个模型拥有多个关联模型，但你希望便捷地获取其中「最新」或「最早」的一个。例如，`User` 模型关联了多个 `Image` 模型，而你希望方便地操作用户最近上传的图片。可以结合 `morphOne` 关联类型和 `ofMany` 系列方法来实现：

```php
/**
 * 获取用户最近的图片。
 */
public function latestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->latestOfMany();
}
```

同样，也可以定义一个方法，检索关联中「最早」的模型，即第一个关联模型：

```php
/**
 * 获取用户最早的图片。
 */
public function oldestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->oldestOfMany();
}
```

默认情况下，`latestOfMany` 和 `oldestOfMany` 方法会基于模型的主键来获取最新或最旧的相关模型，该主键必须是可排序的，但有时你可能希望使用不同的排序条件从更大的关联中获取单个模型。

例如，可以使用 `ofMany` 检索用户获赞最多的图片。`ofMany` 的第一个参数是可排序的列，第二个参数是查询关联模型时使用的聚合函数（`min` 或 `max`）：

```php
/**
 * 获取用户获赞最多的图片。
 */
public function bestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->ofMany('likes', 'max');
}
```

> [!NOTE]
> 也可以构建更复杂的「多记录中的单个关联」。详情请参阅[高级多记录中的单个关联](#advanced-has-one-of-many-relationships)。

<a name="many-to-many-polymorphic-relations"></a>
### 多对多（多态）

<a name="many-to-many-polymorphic-table-structure"></a>
#### 表结构

多对多多态关联比「morph one」和「morph many」关联稍微复杂一些。例如，`Post` 模型和 `Video` 模型可以共享到 `Tag` 模型的多态关联。这样便能将标签统一存放在一张表中，每个标签都可以关联到文章或视频。定义该关联所需的表结构如下：

```text
posts
    id - integer
    name - string

videos
    id - integer
    name - string

tags
    id - integer
    name - string

taggables
    tag_id - integer
    taggable_type - string
    taggable_id - integer
```

> [!NOTE]
> 在深入了解多对多多态关联之前，建议先阅读普通[多对多关联](#many-to-many)的文档。

<a name="many-to-many-polymorphic-model-structure"></a>
#### 模型结构

接下来，在模型中定义关联。`Post` 和 `Video` 模型都需要定义 `tags` 方法，调用 Eloquent 模型基类提供的 `morphToMany` 方法。

`morphToMany` 接受关联模型的类名和「关联名称」。根据中间表的名称及其中的键，本例将关联命名为「taggable」：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphToMany;

class Post extends Model
{
    /**
     * 获取文章的所有标签。
     */
    public function tags(): MorphToMany
    {
        return $this->morphToMany(Tag::class, 'taggable');
    }
}
```

<a name="many-to-many-polymorphic-defining-the-inverse-of-the-relationship"></a>
#### 定义反向关联

接下来，在 `Tag` 模型中为每一种可能的父模型定义方法。在本例中，需要定义 `posts` 和 `videos`，两者都返回 `morphedByMany` 的结果。

`morphedByMany` 接受关联模型的类名和「关联名称」。根据中间表的名称及其中的键，本例将关联命名为「taggable」：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphToMany;

class Tag extends Model
{
    /**
     * 获取拥有此标签的所有文章。
     */
    public function posts(): MorphToMany
    {
        return $this->morphedByMany(Post::class, 'taggable');
    }

    /**
     * 获取拥有此标签的所有视频。
     */
    public function videos(): MorphToMany
    {
        return $this->morphedByMany(Video::class, 'taggable');
    }
}
```

<a name="many-to-many-polymorphic-retrieving-the-relationship"></a>
#### 检索关联

定义数据库表和模型后，就可以通过模型访问关联。例如，使用 `tags` 动态关联属性访问文章的所有标签：

```php
use App\Models\Post;

$post = Post::find(1);

foreach ($post->tags as $tag) {
    // ...
}
```

要通过多态子模型检索父模型，可以访问调用 `morphedByMany` 的方法名。在本例中，就是 `Tag` 模型的 `posts` 或 `videos`：

```php
use App\Models\Tag;

$tag = Tag::find(1);

foreach ($tag->posts as $post) {
    // ...
}

foreach ($tag->videos as $video) {
    // ...
}
```

<a name="custom-polymorphic-types"></a>
### 自定义多态类型

默认情况下，Laravel 使用模型的完全限定类名存储关联模型的「类型」。例如，在前面的一对多示例中，`Comment` 模型可以属于 `Post` 或 `Video` 模型，对应的 `commentable_type` 默认为 `App\Models\Post` 或 `App\Models\Video`。不过，你可能希望将这些值与应用的内部结构解耦。

例如，我们可以使用简单的字符串（如 `post` 和 `video`）而不是使用模型名称作为「类型」。通过这样做，即使模型被重命名，我们数据库中的多态「类型」列值也将保持有效：

```php
use Illuminate\Database\Eloquent\Relations\Relation;

Relation::enforceMorphMap([
    'post' => 'App\Models\Post',
    'video' => 'App\Models\Video',
]);
```

可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `enforceMorphMap`，也可以按需创建单独的服务提供者。

你可以使用模型的 `getMorphClass` 方法在运行时确定给定模型的多态别名。反之，你可以使用 `Relation::getMorphedModel` 方法确定与多态别名关联的完全限定类名：

```php
use Illuminate\Database\Eloquent\Relations\Relation;

$alias = $post->getMorphClass();

$class = Relation::getMorphedModel($alias);
```

> [!WARNING]
> 在向现有应用程序添加「morph map」时，数据库中仍包含完全限定类的每个可多态化的 `*_type` 列值都需要转换为其「映射」名称。

<a name="dynamic-relationships"></a>
### 动态关联

你可以使用 `resolveRelationUsing` 方法在运行时定义 Eloquent 模型之间的关联。虽然在正常应用程序开发中通常不建议使用，但在开发 Laravel 包时偶尔可能会很有用。

`resolveRelationUsing` 方法接受所需的关联名称作为其第一个参数。传递给该方法的第二个参数应该是一个接受模型实例并返回有效的 Eloquent 关联定义的闭包。通常，你应该在 [服务提供者](/docs/{{version}}/providers) 的 boot 方法中配置动态关联：

```php
use App\Models\Order;
use App\Models\Customer;

Order::resolveRelationUsing('customer', function (Order $orderModel) {
    return $orderModel->belongsTo(Customer::class, 'customer_id');
});
```

> [!WARNING]
> 在定义动态关联时，始终为 Eloquent 关联方法提供明确的键名参数。

<a name="querying-relations"></a>
## 查询关联

所有 Eloquent 关联都通过方法定义，因此可以调用这些方法获取关联实例，而不会立即执行查询加载关联模型。此外，各类 Eloquent 关联也都是[查询构造器](/docs/{{version}}/queries)，允许你在最终执行 SQL 查询之前，继续向关联查询链式添加约束。

例如，在一个博客应用中，`User` 模型拥有多个关联的 `Post` 模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    /**
     * 获取用户的所有文章。
     */
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}
```

可以查询 `posts` 关联，并为关联添加额外约束：

```php
use App\Models\User;

$user = User::find(1);

$user->posts()->where('active', 1)->get();
```

关联支持 Laravel [查询构造器](/docs/{{version}}/queries)的所有方法，建议阅读查询构造器文档，了解可用的方法。

<a name="chaining-orwhere-clauses-after-relationships"></a>
#### 在关联后链式调用 `orWhere` 子句

如上例所示，查询关联时可以自由添加约束。不过，链式调用 `orWhere` 时需要注意：`orWhere` 子句与关联约束处于同一逻辑层级：

```php
$user->posts()
    ->where('active', 1)
    ->orWhere('votes', '>=', 100)
    ->get();
```

上例会生成以下 SQL。可以看到，`or` 子句会使查询返回获赞至少 100 次的 _任何_ 文章，不再局限于指定用户：

```sql
select *
from posts
where user_id = ? and active = 1 or votes >= 100
```

通常应使用[逻辑分组](/docs/{{version}}/queries#logical-grouping)，将条件放入括号中：

```php
use Illuminate\Database\Eloquent\Builder;

$user->posts()
    ->where(function (Builder $query) {
        return $query->where('active', 1)
            ->orWhere('votes', '>=', 100);
    })
    ->get();
```

上例会生成以下 SQL。逻辑分组正确地组合了约束，因此查询仍然仅针对指定用户：

```sql
select *
from posts
where user_id = ? and (active = 1 or votes >= 100)
```

<a name="relationship-methods-vs-dynamic-properties"></a>
### 关联方法与动态属性

如果不需要为 Eloquent 关联查询添加额外约束，可以像访问属性一样访问关联。继续使用 `User` 和 `Post` 模型的示例，可以这样访问用户的所有文章：

```php
use App\Models\User;

$user = User::find(1);

foreach ($user->posts as $post) {
    // ...
}
```

动态关联属性采用「延迟加载」，只有实际访问时才加载关联数据。因此，开发者通常会使用[预加载](#eager-loading)，提前加载获取模型后需要访问的关联。预加载能够显著减少加载模型关联所需执行的 SQL 查询。

<a name="querying-relationship-existence"></a>
### 查询关联是否存在

检索模型记录时，可以根据关联是否存在来筛选结果。例如，要获取至少有一条评论的所有博客文章，可以将关联名称传给 `has` 或 `orHas`：

```php
use App\Models\Post;

// 检索至少有一条评论的所有文章……
$posts = Post::has('comments')->get();
```

也可以指定运算符和数量，进一步自定义查询：

```php
// 检索至少有三条评论的所有文章……
$posts = Post::has('comments', '>=', 3)->get();
```

可以使用点号表示法构建嵌套的 `has` 语句。例如，检索至少有一条评论且该评论至少有一张图片的所有文章：

```php
// 检索至少有一条含图片评论的文章……
$posts = Post::has('comments.images')->get();
```

如果需要更灵活的查询，可以使用 `whereHas` 和 `orWhereHas`，为 `has` 查询添加额外约束，例如检查评论内容：

```php
use Illuminate\Database\Eloquent\Builder;

// 检索至少有一条评论内容匹配 code% 的文章……
$posts = Post::whereHas('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
})->get();

// 检索至少有十条评论内容匹配 code% 的文章……
$posts = Post::whereHas('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
}, '>=', 10)->get();
```

> [!WARNING]
> Eloquent 目前不支持跨数据库查询关联是否存在。关联必须位于同一个数据库中。

<a name="many-to-many-relationship-existence-queries"></a>
#### 查询多对多关联是否存在

可以使用 `whereAttachedTo` 查询与指定模型或模型集合存在多对多关联的模型：

```php
$users = User::whereAttachedTo($role)->get();
```

也可以向 `whereAttachedTo` 传入[集合](/docs/{{version}}/eloquent-collections)实例。Laravel 会检索与集合中任意模型存在关联的模型：

```php
$tags = Tag::whereLike('name', '%laravel%')->get();

$posts = Post::whereAttachedTo($tags)->get();
```

<a name="inline-relationship-existence-queries"></a>
#### 内联关联存在性查询

如果只需要在关联查询中添加一个简单的 where 条件来判断关联是否存在，使用 `whereRelation`、`orWhereRelation`、`whereMorphRelation` 和 `orWhereMorphRelation` 会更方便。例如，查询有未审核通过评论的所有文章：

```php
use App\Models\Post;

$posts = Post::whereRelation('comments', 'is_approved', false)->get();
```

与查询构造器的 `where` 方法一样，也可以指定运算符：

```php
$posts = Post::whereRelation(
    'comments', 'created_at', '>=', now()->minus(hours: 1)
)->get();
```

<a name="querying-relationship-absence"></a>
### 查询关联是否不存在

检索模型记录时，也可以根据关联是否不存在来筛选结果。例如，要检索**没有任何评论**的所有博客文章，可以将关联名称传给 `doesntHave` 或 `orDoesntHave`：

```php
use App\Models\Post;

$posts = Post::doesntHave('comments')->get();
```

如果需要更灵活的查询，可以使用 `whereDoesntHave` 和 `orWhereDoesntHave`，为 `doesntHave` 查询添加额外约束，例如检查评论内容：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::whereDoesntHave('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
})->get();
```

可以使用点号表示法查询嵌套关联。例如，以下查询会检索没有评论的文章，以及有评论但没有任何评论来自被封禁用户的文章：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::whereDoesntHave('comments.author', function (Builder $query) {
    $query->where('banned', 1);
})->get();
```

<a name="querying-morph-to-relationships"></a>
### 查询 Morph To 关联

要查询「morph to」关联是否存在，可以使用 `whereHasMorph` 和 `whereDoesntHaveMorph`。第一个参数是关联名称，接下来传入要包含在查询中的关联模型类名，最后可以传入闭包，自定义关联查询：

```php
use App\Models\Comment;
use App\Models\Post;
use App\Models\Video;
use Illuminate\Database\Eloquent\Builder;

// 检索关联文章或视频的标题匹配 code% 的评论……
$comments = Comment::whereHasMorph(
    'commentable',
    [Post::class, Video::class],
    function (Builder $query) {
        $query->where('title', 'like', 'code%');
    }
)->get();

// 检索未关联到标题匹配 code% 的文章的评论……
$comments = Comment::whereDoesntHaveMorph(
    'commentable',
    Post::class,
    function (Builder $query) {
        $query->where('title', 'like', 'code%');
    }
)->get();
```

有时需要根据关联多态模型的「类型」添加查询约束。传给 `whereHasMorph` 的闭包可以接收第二个参数 `$type`，用于判断当前正在构建哪种类型的查询：

```php
use Illuminate\Database\Eloquent\Builder;

$comments = Comment::whereHasMorph(
    'commentable',
    [Post::class, Video::class],
    function (Builder $query, string $type) {
        $column = $type === Post::class ? 'content' : 'title';

        $query->where($column, 'like', 'code%');
    }
)->get();
```

有时需要查询属于某个「morph to」父模型的子模型。可以使用 `whereMorphedTo` 和 `whereNotMorphedTo`，自动确定给定模型对应的多态类型映射。第一个参数是 `morphTo` 关联的名称，第二个参数是关联的父模型：

```php
$comments = Comment::whereMorphedTo('commentable', $post)
    ->orWhereMorphedTo('commentable', $video)
    ->get();
```

<a name="querying-all-morph-to-related-models"></a>
#### 查询所有关联模型

除了传入可能的多态模型数组，也可以使用通配符 `*`，让 Laravel 从数据库中检索所有可能的多态类型。Laravel 会为此额外执行一次查询：

```php
use Illuminate\Database\Eloquent\Builder;

$comments = Comment::whereHasMorph('commentable', '*', function (Builder $query) {
    $query->where('title', 'like', 'foo%');
})->get();
```

<a name="aggregating-related-models"></a>
## 聚合关联模型

<a name="counting-related-models"></a>
### 统计关联模型数量

有时需要统计某个关联的模型数量，但不希望实际加载这些模型。可以使用 `withCount`，它会在返回的模型中添加 `{relation}_count` 属性：

```php
use App\Models\Post;

$posts = Post::withCount('comments')->get();

foreach ($posts as $post) {
    echo $post->comments_count;
}
```

向 `withCount` 传入数组，可以统计多个关联的数量，也可以为查询添加额外约束：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::withCount(['votes', 'comments' => function (Builder $query) {
    $query->where('content', 'like', 'code%');
}])->get();

echo $posts[0]->votes_count;
echo $posts[0]->comments_count;
```

也可以为关联计数结果指定别名，从而对同一个关联进行多次不同的计数：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::withCount([
    'comments',
    'comments as pending_comments_count' => function (Builder $query) {
        $query->where('approved', false);
    },
])->get();

echo $posts[0]->comments_count;
echo $posts[0]->pending_comments_count;
```

<a name="deferred-count-loading"></a>
#### 延迟加载计数

使用 `loadCount`，可以在检索父模型后再加载关联的数量统计：

```php
$book = Book::first();

$book->loadCount('genres');
```

要为计数查询添加额外约束，可以传入以待统计关联名称为键的数组，数组值为接收查询构造器实例的闭包：

```php
$book->loadCount(['reviews' => function (Builder $query) {
    $query->where('rating', 5);
}]);
```

<a name="relationship-counting-and-custom-select-statements"></a>
#### 关联计数与自定义 Select 语句

如果将 `withCount` 与 `select` 结合使用，应在调用 `select` 之后再调用 `withCount`：

```php
$posts = Post::select(['title', 'body'])
    ->withCount('comments')
    ->get();
```

<a name="other-aggregate-functions"></a>
### 其他聚合函数

除了 `withCount`，Eloquent 还提供 `withMin`、`withMax`、`withAvg`、`withSum` 和 `withExists`。这些方法会在返回的模型中添加 `{relation}_{function}_{column}` 属性：

```php
use App\Models\Post;

$posts = Post::withSum('comments', 'votes')->get();

foreach ($posts as $post) {
    echo $post->comments_sum_votes;
}
```

如果希望使用其他名称访问聚合函数的结果，可以指定别名：

```php
$posts = Post::withSum('comments as total_comments', 'votes')->get();

foreach ($posts as $post) {
    echo $post->total_comments;
}
```

与 `loadCount` 一样，这些方法也有延迟加载的版本，允许在已经检索到的 Eloquent 模型上执行这些聚合操作：

```php
$post = Post::first();

$post->loadSum('comments', 'votes');
```

如果将这些聚合方法与 `select` 结合使用，应在调用 `select` 之后再调用聚合方法：

```php
$posts = Post::select(['title', 'body'])
    ->withExists('comments')
    ->get();
```

<a name="counting-related-models-on-morph-to-relationships"></a>
### 统计 Morph To 关联中的关联模型数量

如果希望预加载「morph to」关联，同时统计该关联可能返回的不同实体各自的关联模型数量，可以结合 `with` 和 `morphTo` 关联的 `morphWithCount` 方法。

在本例中，假设 `Photo` 和 `Post` 模型都可以创建 `ActivityFeed` 模型。`ActivityFeed` 定义了名为 `parentable` 的「morph to」关联，用于检索某个 `ActivityFeed` 实例所属的 `Photo` 或 `Post` 父模型。另外，假设 `Photo` 拥有多个 `Tag`，而 `Post` 拥有多个 `Comment`。

现在需要检索 `ActivityFeed` 实例，并为每个实例预加载 `parentable` 父模型，同时获取每张父级图片的标签数量，以及每篇父级文章的评论数量：

```php
use Illuminate\Database\Eloquent\Relations\MorphTo;

$activities = ActivityFeed::with([
    'parentable' => function (MorphTo $morphTo) {
        $morphTo->morphWithCount([
            Photo::class => ['tags'],
            Post::class => ['comments'],
        ]);
    }])->get();
```

<a name="morph-to-deferred-count-loading"></a>
#### 延迟加载计数

假设已经检索到一组 `ActivityFeed` 模型，现在希望为这些动态记录关联的不同 `parentable` 模型加载嵌套关联的数量统计。可以使用 `loadMorphCount`：

```php
$activities = ActivityFeed::with('parentable')->get();

$activities->loadMorphCount('parentable', [
    Photo::class => ['tags'],
    Post::class => ['comments'],
]);
```

<a name="eager-loading"></a>
## 预加载

将 Eloquent 关联作为属性访问时，关联模型采用「延迟加载」，即直到首次访问该属性时，才真正加载关联数据。不过，Eloquent 也支持在查询父模型时「预加载」关联，以缓解「N + 1」查询问题。下面以属于 `Author` 模型的 `Book` 模型为例，说明这个问题：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Book extends Model
{
    /**
     * 获取书籍的作者。
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(Author::class);
    }
}
```

现在检索所有书籍及其作者：

```php
use App\Models\Book;

$books = Book::all();

foreach ($books as $book) {
    echo $book->author->name;
}
```

这个循环会先执行一次查询，检索表中的所有书籍，再为每本书执行一次查询，检索其作者。因此，如果有 25 本书，上面的代码就会执行 26 次查询：1 次获取书籍，另外 25 次分别获取每本书的作者。

使用预加载可以将上述操作减少到两次查询。构建查询时，可以通过 `with` 指定需要预加载的关联：

```php
$books = Book::with('author')->get();

foreach ($books as $book) {
    echo $book->author->name;
}
```

此操作只会执行两次查询：一次获取所有书籍，另一次获取这些书籍的所有作者：

```sql
select * from books

select * from authors where id in (1, 2, 3, 4, 5, ...)
```

<a name="eager-loading-multiple-relationships"></a>
#### 预加载多个关联

有时需要预加载多个不同的关联。只需向 `with` 传入关联名称数组：

```php
$books = Book::with(['author', 'publisher'])->get();
```

<a name="nested-eager-loading"></a>
#### 嵌套预加载

要预加载关联的嵌套关联，可以使用点号表示法。例如，预加载所有书籍的作者，以及作者的所有个人联系人：

```php
$books = Book::with('author.contacts')->get();
```

也可以向 `with` 传入嵌套数组来指定嵌套预加载关联。当需要加载多个嵌套关联时，这种写法更方便：

```php
$books = Book::with([
    'author' => [
        'contacts',
        'publisher',
    ],
])->get();
```

<a name="nested-eager-loading-morphto-relationships"></a>
#### 嵌套预加载 `morphTo` 关联

要预加载 `morphTo` 关联，以及该关联可能返回的不同实体各自的嵌套关联，可以结合 `with` 和 `morphTo` 的 `morphWith` 方法。以下面的模型为例：

```php
<?php

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class ActivityFeed extends Model
{
    /**
     * 获取动态记录的父模型。
     */
    public function parentable(): MorphTo
    {
        return $this->morphTo();
    }
}
```

在本例中，假设 `Event`、`Photo` 和 `Post` 模型都可以创建 `ActivityFeed` 模型。此外，假设 `Event` 属于 `Calendar`，`Photo` 关联到 `Tag`，而 `Post` 属于 `Author`。

根据这些模型定义和关联，可以检索 `ActivityFeed` 实例，并预加载所有 `parentable` 模型及其各自的嵌套关联：

```php
use Illuminate\Database\Eloquent\Relations\MorphTo;

$activities = ActivityFeed::query()
    ->with(['parentable' => function (MorphTo $morphTo) {
        $morphTo->morphWith([
            Event::class => ['calendar'],
            Photo::class => ['tags'],
            Post::class => ['author'],
        ]);
    }])->get();
```

<a name="eager-loading-specific-columns"></a>
#### 预加载指定列

检索关联数据时，不一定需要其中的每一列。因此，Eloquent 允许指定要检索的关联列：

```php
$books = Book::with('author:id,name,book_id')->get();
```

> [!WARNING]
> 使用此功能时，应始终在要检索的列中包含 `id` 列和所有相关外键列。

<a name="eager-loading-by-default"></a>
#### 默认预加载

如果希望检索模型时始终加载某些关联，可以在模型中定义 `$with` 属性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Book extends Model
{
    /**
     * 始终需要加载的关联。
     *
     * @var array
     */
    protected $with = ['author'];

    /**
     * 获取书籍的作者。
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(Author::class);
    }

    /**
     * 获取书籍的分类。
     */
    public function genre(): BelongsTo
    {
        return $this->belongsTo(Genre::class);
    }
}
```

要在单次查询中移除 `$with` 指定的某个关联，可以使用 `without`：

```php
$books = Book::without('author')->get();
```

要在单次查询中覆盖 `$with` 指定的全部关联，可以使用 `withOnly`：

```php
$books = Book::withOnly('genre')->get();
```

<a name="constraining-eager-loads"></a>
### 约束预加载

有时需要在预加载关联的同时，为预加载查询添加额外条件。可以向 `with` 传入关联数组，其中键为关联名称，值为给预加载查询添加约束的闭包：

```php
use App\Models\User;

$users = User::with(['posts' => function ($query) {
    $query->where('title', 'like', '%code%');
}])->get();
```

在本例中，Eloquent 只会预加载 `title` 列包含 `code` 的文章。也可以调用其他[查询构造器](/docs/{{version}}/queries)方法，进一步自定义预加载操作：

```php
$users = User::with(['posts' => function ($query) {
    $query->orderBy('created_at', 'desc');
}])->get();
```

<a name="constraining-eager-loading-of-morph-to-relationships"></a>
#### 约束 `morphTo` 关联的预加载

预加载 `morphTo` 关联时，Eloquent 会执行多次查询，分别获取各类型的关联模型。可以使用 `MorphTo` 关联的 `constrain` 方法，为这些查询分别添加额外约束：

```php
use Illuminate\Database\Eloquent\Relations\MorphTo;

$comments = Comment::with(['commentable' => function (MorphTo $morphTo) {
    $morphTo->constrain([
        Post::class => function ($query) {
            $query->whereNull('hidden_at');
        },
        Video::class => function ($query) {
            $query->where('type', 'educational');
        },
    ]);
}])->get();
```

在本例中，Eloquent 只会预加载未被隐藏的文章，以及 `type` 值为「educational」的视频。

<a name="constraining-eager-loads-with-relationship-existence"></a>
#### 结合关联存在性约束预加载

有时需要检查关联是否存在，同时根据相同条件加载关联。例如，只检索拥有符合指定条件的子 `Post` 模型的 `User` 模型，并预加载这些符合条件的文章。可以使用 `withWhereHas`：

```php
use App\Models\User;

$users = User::withWhereHas('posts', function ($query) {
    $query->where('featured', true);
})->get();
```

<a name="lazy-eager-loading"></a>
### 延迟预加载

有时需要在检索父模型后再预加载关联。例如，动态决定是否加载关联模型时，这种方式很有用：

```php
use App\Models\Book;

$books = Book::all();

if ($condition) {
    $books->load('author', 'publisher');
}
```

要为预加载查询添加额外约束，可以传入以待加载关联名称为键的数组，数组值为接收查询实例的闭包：

```php
$author->load(['books' => function ($query) {
    $query->orderBy('published_date', 'asc');
}]);
```

要仅在关联尚未加载时加载它，可以使用 `loadMissing`：

```php
$book->loadMissing('author');
```

<a name="nested-lazy-eager-loading-morphto"></a>
#### 嵌套延迟预加载与 `morphTo`

要预加载 `morphTo` 关联，以及该关联可能返回的不同实体各自的嵌套关联，可以使用 `loadMorph`。

该方法的第一个参数是 `morphTo` 关联名称，第二个参数是模型与关联对应的数组。以下面的模型为例：

```php
<?php

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class ActivityFeed extends Model
{
    /**
     * 获取动态记录的父模型。
     */
    public function parentable(): MorphTo
    {
        return $this->morphTo();
    }
}
```

在本例中，假设 `Event`、`Photo` 和 `Post` 模型都可以创建 `ActivityFeed` 模型。此外，假设 `Event` 属于 `Calendar`，`Photo` 关联到 `Tag`，而 `Post` 属于 `Author`。

根据这些模型定义和关联，可以检索 `ActivityFeed` 实例，并预加载所有 `parentable` 模型及其各自的嵌套关联：

```php
$activities = ActivityFeed::with('parentable')
    ->get()
    ->loadMorph('parentable', [
        Event::class => ['calendar'],
        Photo::class => ['tags'],
        Post::class => ['author'],
    ]);
```

<a name="automatic-eager-loading"></a>
### 自动预加载

在许多情况下，Laravel 可以自动预加载你访问的关联。要启用自动预加载，请在应用 `AppServiceProvider` 的 `boot` 方法中调用 `Model::automaticallyEagerLoadRelationships`：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Model::automaticallyEagerLoadRelationships();
}
```

启用此功能后，Laravel 会尝试自动加载你访问的、此前尚未加载的关联。以下面的场景为例：

```php
use App\Models\User;

$users = User::all();

foreach ($users as $user) {
    foreach ($user->posts as $post) {
        foreach ($post->comments as $comment) {
            echo $comment->content;
        }
    }
}
```

通常，上面的代码会为每个用户分别查询其文章，再为每篇文章分别查询其评论。不过，启用 `automaticallyEagerLoadRelationships` 后，只要访问已检索用户中任一用户的文章，Laravel 就会为整个用户集合[延迟预加载](#lazy-eager-loading)文章。同样，只要访问任一已检索文章的评论，Laravel 就会为最初检索到的所有文章延迟预加载评论。

如果不想全局启用自动预加载，也可以在某个 Eloquent 集合实例上调用 `withRelationshipAutoloading`，仅为该集合启用此功能：

```php
$users = User::where('vip', true)->get();

return $users->withRelationshipAutoloading();
```

<a name="preventing-lazy-loading"></a>
### 禁止延迟加载

如前所述，预加载关联通常能显著提高应用性能。因此，你也可以让 Laravel 始终禁止关联的延迟加载。只需调用 Eloquent 模型基类提供的 `preventLazyLoading`，通常应在应用 `AppServiceProvider` 类的 `boot` 方法中调用。

`preventLazyLoading` 接受一个可选的布尔参数，表示是否禁止延迟加载。例如，可以只在非生产环境中禁用延迟加载，确保生产代码中即使意外使用了延迟加载关联，应用仍然能够正常运行：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Model::preventLazyLoading(! $this->app->isProduction());
}
```

禁止延迟加载后，如果应用尝试延迟加载任何 Eloquent 关联，Eloquent 会抛出 `Illuminate\Database\LazyLoadingViolationException`。

可以使用 `handleLazyLoadingViolationUsing`，自定义违反延迟加载限制时的处理方式。例如，仅记录日志，而不通过异常中断应用执行：

```php
Model::handleLazyLoadingViolationUsing(function (Model $model, string $relation) {
    $class = $model::class;

    info("Attempted to lazy load [{$relation}] on model [{$class}].");
});
```

<a name="inserting-and-updating-related-models"></a>
## 插入和更新关联模型

<a name="the-save-method"></a>
### `save` 方法

Eloquent 提供了向关联中添加新模型的便捷方法。例如，为文章添加评论时，无需手动设置 `Comment` 模型的 `post_id` 属性，可以直接使用关联的 `save` 方法插入评论：

```php
use App\Models\Comment;
use App\Models\Post;

$comment = new Comment(['message' => 'A new comment.']);

$post = Post::find(1);

$post->comments()->save($comment);
```

注意，这里没有将 `comments` 关联作为动态属性访问，而是调用 `comments` 方法获取关联实例。`save` 会自动为新的 `Comment` 模型设置正确的 `post_id` 值。

要保存多个关联模型，可以使用 `saveMany`：

```php
$post = Post::find(1);

$post->comments()->saveMany([
    new Comment(['message' => 'A new comment.']),
    new Comment(['message' => 'Another new comment.']),
]);
```

`save` 和 `saveMany` 会将给定模型实例持久化到数据库，但不会将新保存的模型添加到父模型内存中已经加载的关联中。如果需要在调用 `save` 或 `saveMany` 后访问关联，可以使用 `refresh` 重新加载模型及其关联：

```php
$post->comments()->save($comment);

$post->refresh();

// 所有评论，包括刚保存的评论……
$post->comments;
```

<a name="the-push-method"></a>
#### 递归保存模型及其关联

要 `save`（保存）模型及其所有关联，可以使用 `push`。在本例中，`Post` 模型、文章的评论以及评论作者都会被保存：

```php
$post = Post::find(1);

$post->comments[0]->message = 'Message';
$post->comments[0]->author->name = 'Author Name';

$post->push();
```

可以使用 `pushQuietly` 保存模型及其关联，而不派发任何事件：

```php
$post->pushQuietly();
```

<a name="the-create-method"></a>
### `create` 方法

除了 `save` 和 `saveMany`，还可以使用 `create`。它接受属性数组，创建模型并将其插入数据库。`save` 与 `create` 的区别在于：`save` 接受完整的 Eloquent 模型实例，而 `create` 接受普通的 PHP `array`。`create` 会返回新创建的模型：

```php
use App\Models\Post;

$post = Post::find(1);

$comment = $post->comments()->create([
    'message' => 'A new comment.',
]);
```

可以使用 `createMany` 创建多个关联模型：

```php
$post = Post::find(1);

$post->comments()->createMany([
    ['message' => 'A new comment.'],
    ['message' => 'Another new comment.'],
]);
```

可以使用 `createQuietly` 和 `createManyQuietly` 创建模型，而不派发任何事件：

```php
$user = User::find(1);

$user->posts()->createQuietly([
    'title' => 'Post title.',
]);

$user->posts()->createManyQuietly([
    ['title' => 'First post.'],
    ['title' => 'Second post.'],
]);
```

也可以使用 `findOrNew`、`firstOrNew`、`firstOrCreate` 和 `updateOrCreate`，[通过关联创建和更新模型](/docs/{{version}}/eloquent#upserts)。

> [!NOTE]
> 使用 `create` 前，请先阅读[批量赋值](/docs/{{version}}/eloquent#mass-assignment)文档。

<a name="updating-belongs-to-relationships"></a>
### Belongs To 关联

要为子模型指定新的父模型，可以使用 `associate`。在本例中，`User` 模型定义了到 `Account` 模型的 `belongsTo` 关联。`associate` 会设置子模型的外键：

```php
use App\Models\Account;

$account = Account::find(10);

$user->account()->associate($account);

$user->save();
```

要从子模型中移除父模型，可以使用 `dissociate` 方法。该方法将关联的外键设置为 `null`：

```php
$user->account()->dissociate();

$user->save();
```

<a name="updating-many-to-many-relationships"></a>
### 多对多关联

<a name="attaching-detaching"></a>
#### 附加 / 分离

Eloquent 还提供了一些方法，使得处理多对多关联更加方便。例如，假设一个用户可以拥有多个角色，而一个角色也可以拥有多个用户。你可以使用 `attach` 方法将一个角色附加到一个用户，通过在关联的中间表中插入一条记录：

```php
use App\Models\User;

$user = User::find(1);

$user->roles()->attach($roleId);
```

当向模型附加关联时，你也可以传递一个包含要插入到中间表的附加数据的数组：

```php
$user->roles()->attach($roleId, ['expires' => $expires]);
```

有时需要从用户中移除一个角色。要移除多对多关联记录，可以使用 `detach` 方法。`detach` 方法将从中间表中删除适当的记录；但是，两个模型将仍然保留在数据库中：

```php
// 从用户中分离一个角色……
$user->roles()->detach($roleId);

// 从用户中分离所有角色……
$user->roles()->detach();
```

为了方便起见，`attach` 和 `detach` 也接受 ID 数组作为输入：

```php
$user = User::find(1);

$user->roles()->detach([1, 2, 3]);

$user->roles()->attach([
    1 => ['expires' => $expires],
    2 => ['expires' => $expires],
]);
```

<a name="syncing-associations"></a>
#### 同步关联

你还可以使用 `sync` 方法构建多对多关联。`sync` 方法接受一个 ID 数组，放置在中间表上。不在给定数组中的任何 ID 将从中间表中删除。因此，在此操作完成后，只有给定数组中的 ID 将存在于中间表中：

```php
$user->roles()->sync([1, 2, 3]);
```

也可以在传入 ID 的同时，提供额外的中间表数据：

```php
$user->roles()->sync([1 => ['expires' => true], 2, 3]);
```

如果希望将相同的中间表值与每个同步模型 ID 一起插入，可以使用 `syncWithPivotValues` 方法：

```php
$user->roles()->syncWithPivotValues([1, 2, 3], ['active' => true]);
```

如果希望保留中间表中已有但未出现在给定数组中的 ID，可以使用 `syncWithoutDetaching`：

```php
$user->roles()->syncWithoutDetaching([1, 2, 3]);
```

<a name="toggling-associations"></a>
#### 切换关联

多对多关联还提供了一个 `toggle` 方法，用于「切换」给定相关模型的附加状态。如果给定的 ID 当前已附加，它将被分离。同样，如果它当前处于分离状态，它将被附加：

```php
$user->roles()->toggle([1, 2, 3]);
```

也可以在传入 ID 的同时，提供额外的中间表数据：

```php
$user->roles()->toggle([
    1 => ['expires' => true],
    2 => ['expires' => true],
]);
```

<a name="transactional-pivot-operations"></a>
#### 事务性中间表操作

上面介绍的中间表操作都有对应的 `OrFail` 版本（`attachOrFail`、`detachOrFail`、`syncOrFail`、`syncWithoutDetachingOrFail` 和 `toggleOrFail`），会将操作放入数据库事务中。如果抛出异常，所有变更都会自动回滚：

```php
$user->roles()->attachOrFail([1, 2, 3]);

$user->roles()->syncOrFail([1, 2, 3]);
```

<a name="updating-a-record-on-the-intermediate-table"></a>
#### 更新中间表记录

如果你需要更新关联的中间表中的现有行，你可以使用 `updateExistingPivot` 方法。该方法接受中间记录外键和要更新的属性数组：

```php
$user = User::find(1);

$user->roles()->updateExistingPivot($roleId, [
    'active' => false,
]);
```

<a name="touching-parent-timestamps"></a>
## 更新父模型时间戳

当一个模型定义了一个 `belongsTo` 或 `belongsToMany` 关联到另一个模型，比如一个 `Comment` 属于一个 `Post`，有时在更新子模型时更新父模型的时间戳是有帮助的。

例如，更新 `Comment` 模型时，可能希望自动更新所属 `Post` 模型的 `updated_at` 时间戳，将其设为当前时间。为此，可以在子模型上使用 `Touches` 特性，指定子模型更新时需要同步更新 `updated_at` 时间戳的关联名称：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Touches;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Touches(['post'])]
class Comment extends Model
{
    /**
     * 获取评论所属的文章。
     */
    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }
}
```

> [!WARNING]
> 只有通过 Eloquent 的 `save` 方法更新子模型时，父模型的时间戳才会更新。
