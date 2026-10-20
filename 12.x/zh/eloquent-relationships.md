
# Eloquent: Relationships

- [简介](#introduction)
- [定义关联](#defining-relationships)
    - [一对一](#one-to-one)
    - [一对多](#one-to-many)
    - [一对多 (反向) / 属于](#one-to-many-inverse)
    - [一对多检索](#has-one-of-many)
    - [远程一对一](#has-one-through)
    - [远程一对多](#has-many-through)
- [作用域关联](#scoped-relationships)
- [多对多关联](#many-to-many)
    - [获取中间表字段](#retrieving-intermediate-table-columns)
    - [通过中间表字段查询过滤](#filtering-queries-via-intermediate-table-columns)
    - [通过 中间表字段排列查询](#ordering-queries-via-intermediate-table-columns)
    - [自定义中间表模型](#defining-custom-intermediate-table-models)
- [多态关联](#polymorphic-relationships)
    - [一对一](#one-to-one-polymorphic-relations)
    - [一对多](#one-to-many-polymorphic-relations)
    - [一对多检索](#one-of-many-polymorphic-relations)
    - [多对多](#many-to-many-polymorphic-relations)
    - [自定义多态模型](#custom-polymorphic-types)
- [动态关联](#dynamic-relationships)
- [查询关联](#querying-relations)
    - [关联方法与动态属性](#relationship-methods-vs-dynamic-properties)
    - [基于存在的关联查询](#querying-relationship-existence)
    - [基于不存在的关联查询](#querying-relationship-absence)
    - [基于多态的关联查询](#querying-morph-to-relationships)
- [统计关联模型](#aggregating-related-models)
    - [关联模型计数](#counting-related-models)
    - [其它统计函数](#other-aggregate-functions)
    - [多态关联数据计数](#counting-related-models-on-morph-to-relationships)
- [预加载](#eager-loading)
    - [约束预加载](#constraining-eager-loads)
    - [延迟预加载](#lazy-eager-loading)
    - [自动预加载](#automatic-eager-loading)
    - [阻止懒加载](#preventing-lazy-loading)
- [插入及更新关联模型](#inserting-and-updating-related-models)
    - [save 方法](#the-save-method)
    - [create 方法](#the-create-method)
    - [属于关联](#updating-belongs-to-relationships)
    - [多对多关联](#updating-many-to-many-relationships)
- [更新父级时间戳](#touching-parent-timestamps)

<a name="introduction"></a>
## 简介

数据库表通常相关互联。例如，一篇博客文章可能有许多评论，或者一个订单对应一个下单用户。 `Eloquent` 让这些关联的管理和使用变得简单，并支持多种常用的关联类型：

<div class="content-list" markdown="1">

- [一对一](#one-to-one)
- [一对多](#one-to-many)
- [多对多](#many-to-many)
- [远程一对一](#has-one-through)
- [远程一对多](#has-many-through)
- [多态一对一](#one-to-one-polymorphic-relations)
- [多态一对多](#one-to-many-polymorphic-relations)
- [多态多对多](#many-to-many-polymorphic-relations)

</div>



<a name="defining-relationships"></a>
## 定义关联关系

Eloquent 关联关系在 Eloquent 模型类中定义为方法。 由于关联关系也充当强大的 [查询构建器](https://laravel.com/docs/laravel/12.x/queries) ，将关联关系定义为方法提供了强大的方法链和查询能力。 例如，我们可以在这个 `posts` 关联关系上链式添加额外的查询约束：

```php
$user->posts()->where('active', 1)->get();
```

但是，在深入使用关联关系之前，让我们先了解如何定义 Eloquent 支持的每种关联关系类型。

<a name="one-to-one"></a>
### 一对一 / Has One

一对一关系是一种非常基础的数据库关系类型。 例如，一个 `User` 模型可能与一个 `Phone` 模型关联。 要定义这种关系，我们将在 `User` 模型上放置一个 `phone` 方法。 `phone` 方法应调用 `hasOne` 方法并返回其结果。 `hasOne` 方法通过模型的 `Illuminate\Database\Eloquent\Model` 基类提供给您的模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOne;

class User extends Model
{
    /**
     * 获取与用户关联的电话
     */
    public function phone(): HasOne
    {
        return $this->hasOne(Phone::class);
    }
}
```

传递给 `hasOne` 方法的第一个参数是相关模型类的名称。 一旦定义了关联关系，我们就可以使用 Eloquent 的动态属性来检索相关记录。 动态属性允许您像访问模型上定义的属性一样访问关联关系方法：

```php
$phone = User::find(1)->phone;
```

Eloquent 根据父模型名称确定关联关系的外键。 在这种情况下，自动假定 `Phone` 模型具有 `user_id` 外键。 如果您希望覆盖此约定，可以向 `hasOne` 方法传递第二个参数：

```php
return $this->hasOne(Phone::class, 'foreign_key');
```

此外，Eloquent 默认假设外键的值应当与父模型主键列的值相匹配。换句话说，Eloquent 会在 `Phone` 记录的 `user_id` 列中，查找与用户 `id` 列相同的值。  
如果你希望在关联中使用非 `id` 或模型 `$primaryKey` 属性作为主键值，可以在 `hasOne` 方法中传递第三个参数：

```php
return $this->hasOne(Phone::class, 'foreign_key', 'local_key');
```

<a name="one-to-one-defining-the-inverse-of-the-relationship"></a>
#### 定义关联的反向关系

上面我们已经能够通过 `User` 模型访问 `Phone` 模型。接下来，我们还需要在 `Phone` 模型上定义一个关联，以便能访问到拥有该手机的用户。
我们可以通过 `belongsTo` 方法来定义 `hasOne` 关系的反向关联：

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

当调用 `user` 方法时，Eloquent 会尝试查找一个 `User` 模型，其 `id` 值与 `Phone` 模型中的 `user_id` 列相匹配。

Eloquent 会通过检查关联方法的名字，并在方法名后追加 `_id`，来推断外键的名称。  
所以在本例中，Eloquent 默认假设 `Phone` 模型中存在 `user_id` 列。  
但是，如果 `Phone` 模型中的外键并不是 `user_id`，你可以在 `belongsTo` 方法中传递第二个参数来自定义外键名称：

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

一对多关系用于定义这样的场景：一个模型作为父模型，可以拥有一个或多个子模型。
例如，一篇博客文章可以有无限多条评论。和其他 Eloquent 关联一样，一对多关系通过在 Eloquent 模型中定义一个方法来实现：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Post extends Model
{
    /**
     * 获取该博客文章的所有评论。
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }
}
```

需要注意，Eloquent 会自动推断 `Comment` 模型的外键列。
按照惯例，Eloquent 会将父模型的名称转换为蛇形命名「snake case」，并在其后加上 `_id`。
因此，在本例中，Eloquent 假设 `Comment` 模型中的外键列为 `post_id`。

当定义好关联方法后，我们就可以通过访问 `comments` 属性，来获取相关文章的 [集合](/docs/laravel/12.x/eloquent-collections)。
需要记住的是，Eloquent 提供了「动态关联属性」，因此我们可以像访问模型属性一样访问关联方法：

```php
use App\Models\Post;

$comments = Post::find(1)->comments;

foreach ($comments as $comment) {
    // ...
}
```


由于所有关联也同时作为查询构建器使用，你可以通过调用 `comments` 方法，并在查询上继续链式添加条件，从而为关联查询添加更多约束：  

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
#### 在子模型上自动加载父模型

即使使用了 Eloquent 预加载，如果在循环子模型时访问其父模型，也可能出现「N + 1」查询问题：  

```php
$posts = Post::with('comments')->get();

foreach ($posts as $post) {
    foreach ($post->comments as $comment) {
        echo $comment->post->title;
    }
}
```

在上例中，即使每个 `Post` 模型的评论已被预加载，仍然会引入「N + 1」查询问题，因为 Eloquent 不会自动在每个子 `Comment` 模型上加载其父 `Post` 模型。  

如果希望 Eloquent 自动将父模型加载到其子模型上，可以在定义 `hasMany` 关联时调用 `chaperone` 方法：  

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Post extends Model
{
    /**
     * 获取该博客文章的所有评论。
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class)->chaperone();
    }
}
```

或者，如果希望在运行时选择性启用父模型的自动加载，可以在预加载关联时调用 `chaperone` 方法：  

```php
use App\Models\Post;

$posts = Post::with([
    'comments' => fn ($comments) => $comments->chaperone(),
])->get();
```


<a name="one-to-many-inverse"></a>
### 一对多（反向） / Belongs To

既然我们可以访问一篇文章的所有评论，现在我们来定义一个关联，让评论可以访问它的父文章。
要定义 `hasMany` 关联的反向关系，可以在子模型上定义一个关联方法，并调用 `belongsTo` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Comment extends Model
{
    /**
     * 获取拥有该评论的文章。
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

在上例中，Eloquent 会尝试查找一个 `Post` 模型，其 `id` 值与 `Comment` 模型中的 `post_id` 列相匹配。

Eloquent 会通过检查关联方法的名称，并在方法名后加上「_」以及父模型主键列名，来确定默认的外键名称。
因此，在本例中，Eloquent 默认假设 `comments` 表中 `Post` 模型的外键列为 `post_id`。  

但是，如果关联的外键不遵循这些约定，你可以在 `belongsTo` 方法中传递第二个参数，自定义外键名称：

```php
/**
 * 获取拥有该评论的文章。
 */
public function post(): BelongsTo
{
    return $this->belongsTo(Post::class, 'foreign_key');
}
```

如果父模型没有使用 `id` 作为主键，或者你希望通过其他列查找关联模型，可以在 `belongsTo` 方法中传递第三个参数，指定父表的自定义键：  

```php
/**
 * 获取拥有该评论的文章。
 */
public function post(): BelongsTo
{
    return $this->belongsTo(Post::class, 'foreign_key', 'owner_key');
}
```


<a name="default-models"></a>
#### 默认模型

`belongsTo`、`hasOne`、`hasOneThrough` 和 `morphOne` 关联允许你定义一个默认模型，当关联为 `null` 时返回该模型。
这种模式通常被称为[空对象模式](https://en.wikipedia.org/wiki/Null_Object_pattern)，可以帮助减少代码中的条件判断。
在下面的示例中，如果 `Post` 模型没有关联任何用户，`user` 关联将返回一个空的 `App\Models\User` 模型：

```php
/**
 * 获取文章的作者。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class)->withDefault();
}
```

如果希望在默认模型中填充属性，可以向 `withDefault` 方法传递一个数组或闭包：

```php
/**
 * 获取文章的作者。
 */
public function user(): BelongsTo
{
    return $this->belongsTo(User::class)->withDefault([
        'name' => 'Guest Author',
    ]);
}

/**
 * 获取文章的作者。
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

你还可以向 `whereBelongsTo` 方法传递一个 [集合](/docs/laravel/12.x/eloquent-collections) 实例。
在这种情况下，Laravel 会获取属于集合中任意父模型的子模型：

```php
$users = User::where('vip', true)->get();

$posts = Post::whereBelongsTo($users)->get();
```


默认情况下，Laravel 会根据模型的类名来确定与给定模型关联的关系；不过，你也可以手动指定关联名称，将其作为第二个参数传递给 `whereBelongsTo` 方法：

```php
$posts = Post::whereBelongsTo($user, 'author')->get();
```

<a name="has-one-of-many"></a>
### 一对多检索

有时，一个模型可能关联多个相关模型，但你希望方便地获取该关系中「最新」或「最旧」的相关模型。例如，`User` 模型可能关联多个 `Order` 模型，但你希望定义一种便捷方式来操作用户最近下的订单。你可以使用 `hasOne` 关联类型结合 `ofMany` 方法来实现：

```php
/**
 * 获取用户最近的订单。
 */
public function latestOrder(): HasOne
{
    return $this->hasOne(Order::class)->latestOfMany();
}
```

同样，你也可以定义一个方法来获取关系中「最旧」的模型：

```php
/**
 * 获取用户最早的订单。
 */
public function oldestOrder(): HasOne
{
    return $this->hasOne(Order::class)->oldestOfMany();
}
```

默认情况下，`latestOfMany` 和 `oldestOfMany` 方法会根据模型的主键来获取最新或最旧的相关模型，该主键必须是可排序的。但是，有时你可能希望根据其他排序条件，从更大的关系集合中获取单个模型。

例如，使用 `ofMany` 方法，你可以获取用户价格最高的订单。`ofMany` 方法接受可排序列作为第一个参数，以及在查询相关模型时应用的聚合函数（`min` 或 `max`）：

```php
/**
 * 获取用户价格最高的订单。
 */
public function largestOrder(): HasOne
{
    return $this->hasOne(Order::class)->ofMany('price', 'max');
}
```

> [!注意]
> 由于 PostgreSQL 不支持对 UUID 列执行 `MAX` 函数，因此目前无法在 PostgreSQL UUID 列上使用 one-of-many 关系。


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
 * 获取用户价格最高的订单。
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
#### 高级 Has One of Many 关联

有时可能需要构建更高级的「has one of many」关联。例如，`Product` 模型可能关联多个 `Price` 模型，即使在发布新价格后，这些价格仍会保留在系统中。此外，该产品的新价格数据可能会提前发布，通过 `published_at` 列在未来某个时间生效。

因此，总结来说，我们需要获取已发布的最新价格，且发布时间不晚于当前时间。另外，如果有两条价格的发布时间相同，我们会优先选择 ID 最大的价格。为实现这一点，我们必须向 `ofMany` 方法传递一个数组，其中包含用于确定最新价格的可排序列。此外，还需要向 `ofMany` 方法传递一个闭包作为第二个参数，该闭包将负责为关联查询添加额外的发布时间约束：

```php
/**
 * 获取产品的当前价格。
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

「has-one-through」关联定义了与另一个模型的一对一关系。不过，这种关系表示声明模型可以通过第三个模型匹配到另一个模型的单个实例。

例如，在一个汽车修理厂应用中，每个 `Mechanic` 模型可能关联一个 `Car` 模型，而每个 `Car` 模型又可能关联一个 `Owner` 模型。虽然技师和车主在数据库中没有直接关系，但技师可以通过 `Car` 模型访问车主。让我们先来看一下定义这种关联所需的数据表：

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

现在我们已经了解了这种关系的数据表结构，接下来在 `Mechanic` 模型中定义关联：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

class Mechanic extends Model
{
    /**
     * 获取汽车的车主。
     */
    public function carOwner(): HasOneThrough
    {
        return $this->hasOneThrough(Owner::class, Car::class);
    }
}
```

传递给 `hasOneThrough` 方法的第一个参数是我们希望访问的最终模型名称，第二个参数是中间模型的名称。

或者，如果在关联涉及的所有模型上都已经定义了相应的关系，你也可以通过调用 `through` 方法并提供这些关系的名称，来更简洁地定义「has-one-through」关联。例如，如果 `Mechanic` 模型有一个 `cars` 关联，而 `Car` 模型有一个 `owner` 关联，那么就可以这样定义一个连接技师和车主的「has-one-through」关联：

```php
// 基于字符串的写法...
return $this->through('cars')->has('owner');

// 动态写法...
return $this->throughCars()->hasOwner();
```


<a name="has-one-through-key-conventions"></a>
#### 键约定

在执行关联查询时，将使用典型的 Eloquent 外键约定。如果你想自定义关联的键，可以将它们作为第三个和第四个参数传递给 `hasOneThrough` 方法。第三个参数是中间模型上的外键名称，第四个参数是最终模型上的外键名称。第五个参数是本地键，而第六个参数是中间模型的本地键：

```php
class Mechanic extends Model
{
    /**
     * 获取汽车的所有者。
     */
    public function carOwner(): HasOneThrough
    {
        return $this->hasOneThrough(
            Owner::class,
            Car::class,
            'mechanic_id', // cars 表上的外键...
            'car_id', // owners 表上的外键...
            'id', // mechanics 表上的本地键...
            'id' // cars 表上的本地键...
        );
    }
}
```

或者，如前所述，如果相关的关联已经在关系中涉及的所有模型上定义好，你可以通过调用 `through` 方法并提供这些关系的名称，流畅地定义一个「has-one-through」关联。这种方法的优点是可以复用现有关联上已经定义的键约定：

```php
// 基于字符串的语法...
return $this->through('cars')->has('owner');

// 动态语法...
return $this->throughCars()->hasOwner();
```

<a name="has-many-through"></a>
### 远程一对多

「has-many-through」关联提供了一种通过中间关联访问远程关联的便捷方式。例如，假设我们正在构建一个类似 [Laravel Cloud](https://cloud.laravel.com) 的部署平台。一个 `Application` 模型可能会通过一个中间的 `Environment` 模型访问多个 `Deployment` 模型。使用这个示例，你可以轻松获取给定应用的所有部署。让我们来看一下定义这个关联所需的表：

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

或者，如果在关联涉及的所有模型上已经定义了相关关系，你可以通过调用 `through` 方法并提供这些关系的名称，流畅地定义一个「has-many-through」关联。  
例如，如果 `Application` 模型有一个 `environments` 关联，而 `Environment` 模型有一个 `deployments` 关联，那么可以这样定义一个连接应用和部署的「has-many-through」关联：

```php
// 基于字符串的语法...
return $this->through('environments')->has('deployments');

// 动态语法...
return $this->throughEnvironments()->hasDeployments();
```

尽管 `Deployment` 模型的表中没有 `application_id` 列，但通过 `hasManyThrough` 关联，仍可以通过 `$application->deployments` 访问应用的部署。要检索这些模型，Eloquent 会检查中间模型 `Environment` 表中的 `application_id` 列。找到相关的环境 ID 后，再用它们查询 `Deployment` 模型的表。

<a name="has-many-through-key-conventions"></a>
#### 键约定

在执行关联查询时，将使用典型的 Eloquent 外键约定。如果你想自定义关联的键，可以将它们作为第三个和第四个参数传递给 `hasManyThrough` 方法。第三个参数是中间模型上的外键名称，第四个参数是最终模型上的外键名称。第五个参数是本地键，第六个参数是中间模型的本地键：

```php
class Application extends Model
{
    public function deployments(): HasManyThrough
    {
        return $this->hasManyThrough(
            Deployment::class,
            Environment::class,
            'application_id', // environments 表上的外键...
            'environment_id', // deployments 表上的外键...
            'id', // applications 表上的本地键...
            'id' // environments 表上的本地键...
        );
    }
}
```


或者，如前所述，如果在关联涉及的所有模型上已经定义了相关关系，你可以通过调用 `through` 方法并提供这些关系的名称，流畅地定义一个「has-many-through」关联。这种方法的优点是可以复用现有关联上已经定义的键约定：

```php
// 基于字符串的语法...
return $this->through('environments')->has('deployments');

// 动态语法...
return $this->throughEnvironments()->hasDeployments();
```

<a name="scoped-relationships"></a>
### 作用域关联

通常会在模型上添加额外的方法来限制关联。例如，你可能会在 `User` 模型上添加一个 `featuredPosts` 方法，它通过额外的 `where` 限制来约束更广泛的 `posts` 关联：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    /**
     * 获取用户的帖子。
     */
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class)->latest();
    }

    /**
     * 获取用户的精选帖子。
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
 * 获取用户的精选帖子。
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

多对多关联比 `hasOne` 和 `hasMany` 关联稍微复杂一些。一个多对多关联的示例是一个用户拥有多个角色，同时这些角色也可能被应用中的其他用户共享。例如，一个用户可能被分配「Author」和「Editor」角色；然而，这些角色也可能分配给其他用户。因此，一个用户有多个角色，一个角色有多个用户。

<a name="many-to-many-table-structure"></a>
#### 表结构

要定义这种关联，需要三个数据库表：`users`、`roles` 和 `role_user`。`role_user` 表的名称来源于相关模型名称的字母顺序，并包含 `user_id` 和 `role_id` 列。该表用作连接用户和角色的中间表。

请记住，由于一个角色可以属于多个用户，我们不能简单地在 `roles` 表上放置 `user_id` 列，这意味着一个角色只能属于单个用户。为了支持角色可以分配给多个用户，需要 `role_user` 表。关联的表结构可以总结如下：

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

多对多关联是通过定义一个方法并返回 `belongsToMany` 方法的结果来实现的。`belongsToMany` 方法由 `Illuminate\Database\Eloquent\Model` 基类提供，该基类被你应用中的所有 Eloquent 模型使用。例如，在 `User` 模型上定义一个 `roles` 方法。传递给该方法的第一个参数是相关模型类的名称：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class User extends Model
{
    /**
     * 属于用户的角色。
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

由于所有关联也可用作查询构建器，你可以通过调用 `roles` 方法并继续在查询上链式添加条件，为关联查询添加更多约束：

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
#### 定义关联的反向关系

要定义多对多关联的「反向关系」，你应在相关模型上定义一个方法，该方法也返回 `belongsToMany` 方法的结果。为了完成我们的用户/角色示例，在 `Role` 模型上定义 `users` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Role extends Model
{
    /**
     * 属于该角色的用户。
     */
    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class);
    }
}
```

如你所见，该关联的定义与 `User` 模型的对应关系完全相同，只是引用了 `App\Models\User` 模型。由于我们复用了 `belongsToMany` 方法，在定义多对多关联的「反向关系」时，所有常用的表名和键自定义选项依然可用。

<a name="retrieving-intermediate-table-columns"></a>
### 获取中间表的列

如你所学，使用多对多关系需要存在中间表。Eloquent 提供了一些非常方便的方法与该表交互。例如，假设我们的 `User` 模型关联了多个 `Role` 模型。访问该关联后，可以通过模型上的 `pivot` 属性访问中间表：

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

> [!警告]  
> 使用 Eloquent 自动维护时间戳的中间表，必须同时包含 `created_at` 和 `updated_at` 时间戳列。

<a name="customizing-the-pivot-attribute-name"></a>
#### 自定义 `pivot` 属性名称

如前所述，可以通过模型上的 `pivot` 属性访问中间表的属性。但是，你可以自定义该属性名称，以更好地反映它在应用中的用途。

例如，如果你的应用中包含可订阅播客的用户，很可能用户与播客之间存在多对多关系。在这种情况下，你可能希望将中间表属性重命名为 `subscription` 而不是 `pivot`。这可以在定义关联时使用 `as` 方法实现：

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

你还可以在定义关联时，使用 `wherePivot`、`wherePivotIn`、`wherePivotNotIn`、`wherePivotBetween`、`wherePivotNotBetween`、`wherePivotNull` 和 `wherePivotNotNull` 方法，对 `belongsToMany` 关联查询返回的结果进行筛选：

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

你可以使用 `orderByPivot` 方法对 `belongsToMany` 关联查询返回的结果进行排序。在下面的例子中，我们将检索用户的所有最新徽章：

```php
return $this->belongsToMany(Badge::class)
    ->where('rank', 'gold')
    ->orderByPivot('created_at', 'desc');
```

<a name="defining-custom-intermediate-table-models"></a>
### 定义自定义中间表模型

如果你希望为多对多关联的中间表定义自定义模型，可以在定义关联时调用 `using` 方法。自定义 pivot 模型允许你在 pivot 模型上定义额外的行为，例如方法和类型转换。

自定义多对多 pivot 模型应继承 `Illuminate\Database\Eloquent\Relations\Pivot` 类，而自定义多态多对多 pivot 模型应继承 `Illuminate\Database\Eloquent\Relations\MorphPivot` 类。例如，我们可以定义一个 `Role` 模型，它使用自定义的 `RoleUser` pivot 模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Role extends Model
{
    /**
     * The users that belong to the role.
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

> [!警告]
> Pivot 模型不能使用 `SoftDeletes` trait。如果你需要对 pivot 记录进行软删除，请考虑将 pivot 模型转换为实际的 Eloquent 模型。


<a name="custom-pivot-models-and-incrementing-ids"></a>
#### 自定义 Pivot 模型与自增 ID

如果你定义了一个使用自定义 pivot 模型的多对多关系，并且该 pivot 模型具有自增主键，你应该确保自定义 pivot 模型类定义了一个 `incrementing` 属性，并将其设置为 `true`。

```php
/**
 * 指示 ID 是否自增。
 *
 * @var bool
 */
public $incrementing = true;
```

<a name="polymorphic-relationships"></a>
## 多态关系

多态关系允许子模型通过单一关联属于多种类型的模型。例如，假设你正在构建一个应用程序，允许用户分享博客文章和视频。在这样的应用中，`Comment` 模型可能同时属于 `Post` 和 `Video` 模型。

<a name="one-to-one-polymorphic-relations"></a>
### 一对一（多态）

<a name="one-to-one-polymorphic-table-structure"></a>
#### 表结构

一对一多态关系类似于典型的一对一关系；然而，子模型可以通过单一关联属于多种类型的模型。例如，博客 `Post` 和 `User` 可能共享对 `Image` 模型的多态关系。使用一对一多态关系可以让你拥有一个唯一的图像表，这些图像可以关联到文章和用户。首先，让我们查看表结构：

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
    imageable_id - integer
    imageable_type - string
```

请注意 `images` 表上的 `imageable_id` 和 `imageable_type` 列。`imageable_id` 列将包含文章或用户的 ID 值，而 `imageable_type` 列将包含父模型的类名。Eloquent 使用 `imageable_type` 列来确定在访问 `imageable` 关系时返回哪种「类型」的父模型。在此情况下，该列将包含 `App\Models\Post` 或 `App\Models\User`。


<a name="one-to-one-polymorphic-model-structure"></a>
#### 模型结构

接下来，让我们查看构建此关系所需的模型定义：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class Image extends Model
{
    /**
     * 获取父级 imageable 模型（用户或文章）。
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
#### 获取关系

定义数据库表和模型后，你可以通过模型访问这些关系。例如，要获取文章的图片，可以访问 `image` 动态关系属性：

```php
use App\Models\Post;

$post = Post::find(1);

$image = $post->image;
```

你可以通过访问调用 `morphTo` 方法的方法名来获取多态模型的父级。在本例中，该方法是 `Image` 模型上的 `imageable` 方法，因此我们将以动态关系属性的方式访问该方法：

```php
use App\Models\Image;

$image = Image::find(1);

$imageable = $image->imageable;
```

`Image` 模型上的 `imageable` 关系将根据拥有图片的模型类型返回 `Post` 或 `User` 实例。

<a name="morph-one-to-one-key-conventions"></a>
#### 键的约定

如有必要，你可以指定多态子模型使用的「id」和「type」列的名称。如果这样做，请确保始终将关系名称作为第一个参数传递给 `morphTo` 方法。通常，该值应与方法名匹配，因此你可以使用 PHP 的 `__FUNCTION__` 常量：

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

一对多多态关系类似于典型的一对多关系；但是，子模型可以通过单一关联属于多种类型的模型。例如，假设你的应用用户可以对文章和视频进行“评论”。使用多态关系，你可以使用单个 `comments` 表存储文章和视频的评论。首先，让我们查看构建此关系所需的表结构：

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
    commentable_id - integer
    commentable_type - string
```

<a name="one-to-many-polymorphic-model-structure"></a>
#### 模型结构

接下来，让我们查看构建此关系所需的模型定义：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class Comment extends Model
{
    /**
     * 获取父级 commentable 模型（文章或视频）。
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
#### 获取关系

定义数据库表和模型后，你可以通过模型的动态关系属性访问这些关系。例如，要访问文章的所有评论，可以使用 `comments` 动态属性：

```php
use App\Models\Post;

$post = Post::find(1);

foreach ($post->comments as $comment) {
    // ...
}
```


你可以通过访问调用 `morphTo` 方法的名称来获取多态子模型的父模型。在这里，该方法是 `Comment` 模型上的 `commentable` 方法。因此，我们可以将该方法作为动态关系属性访问，以获取评论的父模型：

```php
use App\Models\Comment;

$comment = Comment::find(1);

$commentable = $comment->commentable;
```

`Comment` 模型上的 `commentable` 关系将返回 `Post` 或 `Video` 实例，这取决于评论所属的父模型类型。

<a name="polymorphic-automatically-hydrating-parent-models-on-children"></a>
#### 在子模型上自动填充父模型

即使使用 Eloquent 预加载，如果在循环子模型时尝试访问子模型的父模型，也可能出现「N + 1」查询问题：

```php
$posts = Post::with('comments')->get();

foreach ($posts as $post) {
    foreach ($post->comments as $comment) {
        echo $comment->commentable->title;
    }
}
```

在上例中，引入了「N + 1」查询问题，因为尽管每个 `Post` 模型的评论已经被预加载，但 Eloquent 并不会自动在每个子 `Comment` 模型上填充父 `Post`。

如果希望 Eloquent 自动将父模型填充到子模型上，可以在定义 `morphMany` 关系时调用 `chaperone` 方法：

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

或者，如果希望在运行时选择性地启用自动父模型填充，可以在预加载关系时调用 `chaperone` 方法：

```php
use App\Models\Post;

$posts = Post::with([
    'comments' => fn ($comments) => $comments->chaperone(),
])->get();
```


<a name="one-of-many-polymorphic-relations"></a>
### 多个中取一个 (多态)

有时，一个模型可能关联多个相关模型，但你希望轻松的获取关系中的「最新」或「最旧」相关模型。例如，`User`模型可能与多个 `Image` 模型相关联，但你可能希望定义一种便捷的方式来操作用户上传的最新图片。你可以使用 `morphOne` 关系类型结合 `ofMany` 方法来实现：

```php
/**
 * Get the user's most recent image.
 */
public function latestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->latestOfMany();
}
```

同样的，你可以定义一个方法来获取关系中「最旧」或第一个相关模型：

```php
/**
 * Get the user's oldest image.
 */
public function oldestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->oldestOfMany();
}
```

默认情况下，`latestOfMany` 和 `oldestOfMany` 方法会基于模型的主键来获取最新或最旧的相关模型，该主键必须是可排序的，但有时你可能希望使用不同的排序条件从更大的关系中获取单个模型。

例如，使用 `ofMany` 方法，你可以获取用户最多「点赞」的图片，`ofMany` 方法接受可排序列作为第一个参数，并在查询相关模型时应用哪种聚合函数（min 或 max）：

```php
/**
 * Get the user's most popular image.
 */
public function bestImage(): MorphOne
{
    return $this->morphOne(Image::class, 'imageable')->ofMany('likes', 'max');
}
```

> [注意]
>可以构建更复杂的「多个中的一个」关系。有关更多信息，请参阅[一个中的多个文档](#advanced-has-one-of-many-relationships).



<a name="many-to-many-polymorphic-relations"></a>
### 多对多（多态）

<a name="many-to-many-polymorphic-table-structure"></a>
#### 表结构

多对多多态关系比「morph one」和「morph many」关系稍微复杂一些。例如，`Post` 模型和 `Video` 模型可以共享与 `Tag` 模型的多态关系。在这种情况下使用多对多多态关系，你的应用程序可以拥有一个包含可与帖子或视频关联的唯一标签的单个表。首先，让我们看一下构建这种关系所需的表结构：


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
    taggable_id - integer
    taggable_type - string
```

> [!注意]
> 在深入研究多对多多态关系之前，你可能会从阅读关于典型 [多对多关系](#many-to-many)的文档中受益。.

<a name="many-to-many-polymorphic-model-structure"></a>
#### 模型结构

接下来，我们准备在模型上定义关系。  `Post` 和  `Video` 模型都将包含一个  `tags` 方法，该方法调用基础 Eloquent 模型类提供的 `morphToMany` 方法 。

 `morphToMany` 方法接受相关模型的名称以及「关系名称」。根据我们分配给中间表名称及其包含的键的名称，我们将该关系称为「taggable」：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphToMany;

class Post extends Model
{
    /**
     *  获取该帖子的所有标签
     */
    public function tags(): MorphToMany
    {
        return $this->morphToMany(Tag::class, 'taggable');
    }
}
```



<a name="many-to-many-polymorphic-defining-the-inverse-of-the-relationship"></a>
#### 定义反向关系

接下来，在 Tag 模型上，你应该为每个可能的父模型定义一个方法。因此，在这个例子中，我们将定义一个  `posts`  方法和一个 `videos` 方法。这两个方法都应该返回 `morphedByMany` 方法的结果。

`morphedByMany` 方法接受相关模型的名称以及「关系名称」。根据我们分配给中间表名称及其包含的键的名称，我们将该关系称为「taggable」：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphToMany;

class Tag extends Model
{
    /**
     *  获取分配了该标签的所有帖子。
     */
    public function posts(): MorphToMany
    {
        return $this->morphedByMany(Post::class, 'taggable');
    }

    /**
     * 获取分配了该标签的所有视频。
     */
    public function videos(): MorphToMany
    {
        return $this->morphedByMany(Video::class, 'taggable');
    }
}
```

<a name="many-to-many-polymorphic-retrieving-the-relationship"></a>
#### 获取关系


一旦定义了数据库表和模型，你可以通过你的模型访问关系。例如，要访问帖子的所有标签，你可以使用 `tags` 动态关系属性：

```php
use App\Models\Post;

$post = Post::find(1);

foreach ($post->tags as $tag) {
    // ...
}
```

你可以通过访问调用了 `morphedByMany` 方法的方法名，从多态子模型中获取多态关系的父模型。在这种情况下，就是 `Tag` 模型上的 `posts` 或 `videos` 方法：

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


默认情况下，Laravel 将使用完全限定的类名来存储相关模型的「类型」。例如，考虑上面的一对多关系示例，其中 `Comment`  模型可以属于 `Post` 或 `Video` 模型，默认的 c`ommentable_type` 分别为 `App\Models\Post` 或 `App\Models\Video`。然而，你可能希望将这些值与应用程序的内部结构解耦。

例如，我们可以使用简单的字符串（如 `post` 和 `video`）而不是使用模型名称作为「类型」。通过这样做，即使模型被重命名，我们数据库中的多态「类型」列值也将保持有效：

```php
use Illuminate\Database\Eloquent\Relations\Relation;

Relation::enforceMorphMap([
    'post' => 'App\Models\Post',
    'video' => 'App\Models\Video',
]);
```

你可以在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `enforceMorphMap` 方法，或者也可以创建一个单独的服务提供程序。

你可以使用模型的 `getMorphClass` 方法在运行时确定给定模型的多态别名。反之，你可以使用 `Relation::getMorphedModel` 方法确定与多态别名关联的完全限定类名：

```php
use Illuminate\Database\Eloquent\Relations\Relation;

$alias = $post->getMorphClass();

$class = Relation::getMorphedModel($alias);
```

> [!警告]
> 在向现有应用程序添加「morph map」时，数据库中仍包含完全限定类的每个可多态化的 `*_type` 列值都需要转换为其「映射」名称。

<a name="dynamic-relationships"></a>
### 动态关系

你可以使用 `resolveRelationUsing` 方法在运行时定义 Eloquent 模型之间的关系。虽然在正常应用程序开发中通常不建议使用，但在开发 Laravel 包时偶尔可能会很有用。




`resolveRelationUsing` 方法接受所需的关系名称作为其第一个参数。传递给该方法的第二个参数应该是一个接受模型实例并返回有效的 Eloquent 关系定义的闭包。通常，你应该在 [服务提供者](/docs/laravel/12.x/providers) 的 boot 方法中配置动态关系：


```php
use App\Models\Order;
use App\Models\Customer;

Order::resolveRelationUsing('customer', function (Order $orderModel) {
    return $orderModel->belongsTo(Customer::class, 'customer_id');
});
```

> [!WARNING]
> 在定义动态关系时，始终为 Eloquent 关系方法提供明确的键名参数。

<a name="querying-relations"></a>
## 查询关系



由于所有 Eloquent 关系都是通过方法定义的，你可以调用这些方法以获取关系的实例，而无需实际执行查询来加载相关模型。此外，所有类型的 Eloquent 关系也充当 [查询构建器](/docs/laravel/12.x/queries)，允许你在最终执行 SQL 查询之前继续在关系查询上链约束。

例如，想象一个博客应用程序，其中 `User` 模型有许多关联的 `Post` 模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    /**
     * 获取用户的所有帖子。
     */
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}
```

你可以查询 `posts` 关系并向关系添加额外约束，如下所示：

```php
use App\Models\User;

$user = User::find(1);

$user->posts()->where('active', 1)->get();
```


你可以在关系上使用 Laravel [查询构建器](/docs/laravel/12.x/queries) 的任何方法，因此请务必查阅查询构建器文档，了解所有可用的方法。



#### 在关系后链式调用 `orWhere` 条件

如上例所示，你可以在查询关系时自由添加额外的约束条件。然而，在关系上链式调用 `orWhere` 时需要小心，因为 `orWhere` 条件会在逻辑上与关系约束处于同一级别：

```php
$user->posts()
    ->where('active', 1)
    ->orWhere('votes', '>=', 100)
    ->get();
```

上面的示例将生成如下 SQL。可以看到，`or` 条件会指示查询返回**任何**投票数大于 100 的帖子。查询不再局限于特定用户：

```sql
select *
from posts
where user_id = ? and active = 1 or votes >= 100
```

在大多数情况下，你应该使用 [逻辑分组](/docs/laravel/12.x/queries#logical-grouping) 将条件检查用括号分组：

```php
use Illuminate\Database\Eloquent\Builder;

$user->posts()
    ->where(function (Builder $query) {
        return $query->where('active', 1)
            ->orWhere('votes', '>=', 100);
    })
    ->get();
```

上面的示例将生成如下 SQL。注意逻辑分组已正确地将约束条件分组，查询仍然局限于特定用户：

```sql
select *
from posts
where user_id = ? and (active = 1 or votes >= 100)
```

### 关系方法 vs 动态属性

如果你不需要给 Eloquent 关系查询添加额外约束条件，你可以像访问属性一样访问关系。例如，继续使用我们的 `User` 和 `Post` 示例模型，我们可以这样访问某个用户的所有帖子：

```php
use App\Models\User;

$user = User::find(1);

foreach ($user->posts as $post) {
    // ...
}
```



动态关系属性执行的是“**延迟加载（lazy loading）**”，也就是说，它们只有在你实际访问它们时才会加载关系数据。正因为如此，开发者通常会使用 [**预加载（eager loading**)](#eager-loading) 来提前加载那些在模型加载后已知会被访问的关系。预加载可以显著减少加载模型关系时必须执行的 SQL 查询数量。

### 查询关系是否存在

在检索模型记录时，你可能希望根据关系是否存在来限制结果。例如，假设你想检索所有至少有一个评论的博客文章。为此，你可以将关系名称传递给 `has` 和 `orHas` 方法：

```php
use App\Models\Post;

// 检索所有至少有一个评论的文章...
$posts = Post::has('comments')->get();
```

你还可以指定操作符和计数值以进一步自定义查询：

```php
// 检索所有评论数大于等于三的文章...
$posts = Post::has('comments', '>=', 3)->get();
```

嵌套的 `has` 语句可以使用“点（dot）”表示法构建。例如，你可以检索所有至少有一个评论且该评论至少有一张图片的文章：

```php
// 检索至少有一个评论且评论中有图片的文章...
$posts = Post::has('comments.images')->get();
```

如果你需要更强大的功能，可以使用 `whereHas` 和 `orWhereHas` 方法，在 `has` 查询上定义额外的查询约束，例如检查评论的内容：

```php
use Illuminate\Database\Eloquent\Builder;

// 检索至少有一个评论且内容包含类似 code% 的文章...
$posts = Post::whereHas('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
})->get();

// 检索至少有十个评论且内容包含类似 code% 的文章...
$posts = Post::whereHas('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
}, '>=', 10)->get();
```

> [!警告]
> Eloquent 目前不支持跨数据库查询关系是否存在。关系必须存在于同一个数据库中。



#### 多对多关系存在性查询

`whereAttachedTo` 方法可用于查询那些与某个模型或模型集合存在多对多关联的模型：

```php
$users = User::whereAttachedTo($role)->get();
```

你也可以向 `whereAttachedTo` 方法提供一个 [集合](/docs/laravel/12.x/eloquent-collections) 实例。这样做时，Laravel 会检索与集合中任意模型关联的模型：

```php
$tags = Tag::whereLike('name', '%laravel%')->get();

$posts = Post::whereAttachedTo($tags)->get();
```

#### 内联关系存在性查询

如果你希望通过一个简单的 `where` 条件查询关系是否存在，使用 `whereRelation`、`orWhereRelation`、`whereMorphRelation` 和 `orWhereMorphRelation` 方法会更加方便。例如，我们可以查询所有有未批准评论的文章：

```php
use App\Models\Post;

$posts = Post::whereRelation('comments', 'is_approved', false)->get();
```

当然，像调用查询构建器的 `where` 方法一样，你也可以指定操作符：

```php
$posts = Post::whereRelation(
    'comments', 'created_at', '>=', now()->subHour()
)->get();
```

### 查询关系不存在

在检索模型记录时，你可能希望根据关系不存在来限制结果。例如，假设你想检索所有**没有任何评论**的博客文章。为此，你可以将关系名称传递给 `doesntHave` 和 `orDoesntHave` 方法：

```php
use App\Models\Post;

$posts = Post::doesntHave('comments')->get();
```



如果你需要更强大的功能，可以使用 `whereDoesntHave` 和 `orWhereDoesntHave` 方法，为 `doesntHave` 查询添加额外的约束条件，例如检查评论的内容：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::whereDoesntHave('comments', function (Builder $query) {
    $query->where('content', 'like', 'code%');
})->get();
```

你可以使用“点（dot）”表示法对嵌套关系执行查询。例如，下面的查询将检索所有没有评论的文章，以及那些有评论但评论作者都不是被禁止用户的文章：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::whereDoesntHave('comments.author', function (Builder $query) {
    $query->where('banned', 1);
})->get();
```

### 查询 Morph To 关系

要查询 “morph to” 关系是否存在，你可以使用 `whereHasMorph` 和 `whereDoesntHaveMorph` 方法。这些方法的第一个参数是关系名称。接下来，方法接受你希望在查询中包含的相关模型名称。最后，你可以提供一个闭包来自定义关系查询：

```php
use App\Models\Comment;
use App\Models\Post;
use App\Models\Video;
use Illuminate\Database\Eloquent\Builder;

// 检索与标题类似 code% 的文章或视频关联的评论...
$comments = Comment::whereHasMorph(
    'commentable',
    [Post::class, Video::class],
    function (Builder $query) {
        $query->where('title', 'like', 'code%');
    }
)->get();

// 检索与标题不类似 code% 的文章关联的评论...
$comments = Comment::whereDoesntHaveMorph(
    'commentable',
    Post::class,
    function (Builder $query) {
        $query->where('title', 'like', 'code%');
    }
)->get();
```



你有时可能需要根据关联多态模型的“类型”添加查询约束。传递给 `whereHasMorph` 方法的闭包可以接收 `$type` 作为第二个参数。这个参数允许你检查正在构建的查询的“类型”：

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

有时，你可能希望查询 “morph to” 关系父模型的子模型。你可以使用 `whereMorphedTo` 和 `whereNotMorphedTo` 方法来实现，它们会自动为给定模型确定正确的 morph 类型映射。这些方法的第一个参数是 `morphTo` 关系的名称，第二个参数是相关的父模型：

```php
$comments = Comment::whereMorphedTo('commentable', $post)
    ->orWhereMorphedTo('commentable', $video)
    ->get();
```

#### 查询所有关联模型

你也可以不传递多态模型数组，而是提供 `*` 作为通配符值。这会指示 Laravel 从数据库中检索所有可能的多态类型。Laravel 将执行一个额外的查询来完成此操作：

```php
use Illuminate\Database\Eloquent\Builder;

$comments = Comment::whereHasMorph('commentable', '*', function (Builder $query) {
    $query->where('title', 'like', 'foo%');
})->get();
```

## 聚合关联模型

### 统计关联模型数量

有时你可能希望统计某个关系的关联模型数量，而不实际加载这些模型。为此，你可以使用 `withCount` 方法。`withCount` 方法会在返回的模型上添加一个 `{relation}_count` 属性：

```php
use App\Models\Post;

$posts = Post::withCount('comments')->get();

foreach ($posts as $post) {
    echo $post->comments_count;
}
```



通过向 `withCount` 方法传递数组，你可以为多个关系添加“计数”，同时还可以为查询添加额外约束：

```php
use Illuminate\Database\Eloquent\Builder;

$posts = Post::withCount(['votes', 'comments' => function (Builder $query) {
    $query->where('content', 'like', 'code%');
}])->get();

echo $posts[0]->votes_count;
echo $posts[0]->comments_count;
```

你也可以为关系计数结果指定别名，从而在同一个关系上进行多个计数：

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

#### 延迟加载计数

使用 `loadCount` 方法，你可以在父模型已经被检索之后再加载关系计数：

```php
$book = Book::first();

$book->loadCount('genres');
```

如果你需要在计数查询上设置额外约束，可以传递一个以要计数的关系为键的数组。数组的值应该是接收查询构建器实例的闭包：

```php
$book->loadCount(['reviews' => function (Builder $query) {
    $query->where('rating', 5);
}])
```

#### 关系计数与自定义 `select` 语句

如果你将 `withCount` 与 `select` 语句结合使用，请确保在调用 `select` 方法之后再调用 `withCount`：

```php
$posts = Post::select(['title', 'body'])
    ->withCount('comments')
    ->get();
```

### 其他聚合函数

除了 `withCount` 方法之外，Eloquent 还提供了 `withMin`、`withMax`、`withAvg`、`withSum` 和 `withExists` 方法。这些方法会在返回的模型上添加 `{relation}_{function}_{column}` 属性：

```php
use App\Models\Post;

$posts = Post::withSum('comments', 'votes')->get();

foreach ($posts as $post) {
    echo $post->comments_sum_votes;
}
```



如果你希望使用另一个名称访问聚合函数的结果，你可以指定自己的别名：

```php
$posts = Post::withSum('comments as total_comments', 'votes')->get();

foreach ($posts as $post) {
    echo $post->total_comments;
}
```

像 `loadCount` 方法一样，这些方法也有延迟版本可用。这些额外的聚合操作可以在已经检索到的 Eloquent 模型上执行：

```php
$post = Post::first();

$post->loadSum('comments', 'votes');
```

如果你将这些聚合方法与 `select` 语句结合使用，请确保在调用 `select` 方法之后再调用聚合方法：

```php
$posts = Post::select(['title', 'body'])
    ->withExists('comments')
    ->get();
```

### 在 Morph To 关系上统计关联模型

如果你希望对 “morph to” 关系进行预加载，同时统计该关系可能返回的各种实体的关联模型数量，你可以将 `with` 方法与 `morphTo` 关系的 `morphWithCount` 方法结合使用。

在此示例中，假设 `Photo` 和 `Post` 模型可能创建 `ActivityFeed` 模型。假设 `ActivityFeed` 模型定义了一个名为 `parentable` 的 “morph to” 关系，使我们可以检索给定 `ActivityFeed` 实例的父级 `Photo` 或 `Post` 模型。另外，假设 `Photo` 模型 “拥有多个” `Tag` 模型，而 `Post` 模型 “拥有多个” `Comment` 模型。

现在，假设我们希望检索 `ActivityFeed` 实例，并为每个 `ActivityFeed` 实例预加载其 `parentable` 父模型。此外，我们希望检索每个父级照片关联的标签数量，以及每个父级文章关联的评论数量：

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



### 延迟计数加载

假设我们已经检索到了一组 `ActivityFeed` 模型，现在我们希望为与这些动态信息关联的各种 `parentable` 模型加载其**嵌套关系的数量统计**。你可以使用 `loadMorphCount` 方法来完成这一点：

```php
$activities = ActivityFeed::with('parentable')->get();

$activities->loadMorphCount('parentable', [
    Photo::class => ['tags'],
    Post::class => ['comments'],
]);
```

## 预加载

当你以属性的方式访问 Eloquent 关系时，相关模型会被“**延迟加载（lazy loaded）**”。这意味着关系数据实际上直到你第一次访问该属性时才会被加载。
然而，Eloquent 允许你在查询父模型时就“**预加载（eager load）**”这些关系。预加载可以缓解 **N + 1 查询问题**。
为了说明 N + 1 查询问题，假设有一个 `Book` 模型，它“**属于（belongs to）**”一个 `Author` 模型：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Book extends Model
{
    /**
     * 获取撰写该书籍的作者
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(Author::class);
    }
}
```

现在，让我们获取所有书籍以及它们对应的作者：

```php
use App\Models\Book;

$books = Book::all();

foreach ($books as $book) {
    echo $book->author->name;
}
```

这个循环将会执行一次查询来获取数据库表中的所有书籍，然后**为每一本书再执行一次查询**以获取该书的作者。
因此，如果我们有 25 本书，上述代码将会运行 **26 次查询**：
一次用于最初获取书籍数据，另外 25 次用于分别获取每本书的作者
幸运的是，我们可以使用**预加载**将该操作减少到仅 **两次查询**。在构建查询时，你可以使用 `with` 方法指定需要预加载的关系：

```php
$books = Book::with('author')->get();

foreach ($books as $book) {
    echo $book->author->name;
}
```



对于该操作，只会执行 **两条查询** ——
一条查询用于获取所有书籍，另一条查询用于获取这些书籍对应的所有作者：

```sql
select * from books

select * from authors where id in (1, 2, 3, 4, 5, ...)
```

#### 预加载多个关系

有时你可能需要预加载多个不同的关系。为此，只需向 `with` 方法传入一个关系数组即可：

```php
$books = Book::with(['author', 'publisher'])->get();
```

#### 嵌套预加载

如果要预加载某个关系的关系，你可以使用“**点语法（dot syntax）**”。例如，下面的示例中，我们将预加载所有书籍的作者，以及作者的所有个人联系方式：

```php
$books = Book::with('author.contacts')->get();
```

或者，你也可以通过向 `with` 方法提供一个**嵌套数组**来指定嵌套的预加载关系。当需要预加载多个嵌套关系时，这种方式会更加方便：

```php
$books = Book::with([
    'author' => [
        'contacts',
        'publisher',
    ],
])->get();
```

#### 嵌套预加载 `morphTo` 关系（Nested Eager Loading `morphTo` Relationships）

如果你希望预加载一个 `morphTo` 关系，同时还预加载该关系可能返回的各个实体上的嵌套关系，你可以将 `with` 方法与 `morphTo` 关系的 `morphWith` 方法结合使用。

为了更好地说明这种方法，下面我们来看一个模型示例：

```php
<?php

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class ActivityFeed extends Model
{
    /**
     * 获取活动动态记录的父模型
     */
    public function parentable(): MorphTo
    {
        return $this->morphTo();
    }
}
```



在这个示例中，假设 `Event`、`Photo` 和 `Post` 模型都可能创建 `ActivityFeed` 模型。此外，假设 `Event` 模型属于（`belongs to`）一个 `Calendar` 模型，`Photo` 模型与 `Tag` 模型相关联，而 `Post` 模型属于（`belongs to`）一个 `Author` 模型。

基于这些模型定义和关系，我们可以检索 `ActivityFeed` 模型实例，并预加载所有 `parentable` 模型及其各自对应的嵌套关系：

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

#### 预加载指定列（Eager Loading Specific Columns）

在检索关系数据时，你并不总是需要关系中的每一个字段。因此，Eloquent 允许你指定希望检索的关系字段：

```php
$books = Book::with('author:id,name,book_id')->get();
```

> [!警告]
> 当使用此特性时，你应当始终在要检索的字段列表中包含 `id` 字段以及任何相关的外键字段。

#### 默认预加载（Eager Loading by Default）

有时，你可能希望在检索模型时**始终**加载某些关系。为此，你可以在模型中定义一个 `$with` 属性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Book extends Model
{
    /**
     * 应始终被加载的关系
     *
     * @var array
     */
    protected $with = ['author'];

    /**
     * 获取撰写该书籍的作者
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(Author::class);
    }

    /**
     * 获取书籍的分类
     */
    public function genre(): BelongsTo
    {
        return $this->belongsTo(Genre::class);
    }
}
```



如果你希望在**单次查询中**从 `$with` 属性中移除某一个关系项，可以使用 `without` 方法：

```php
$books = Book::without('author')->get();
```

如果你希望在**单次查询中**覆盖 `$with` 属性中的**所有关系项**，可以使用 `withOnly` 方法：

```php
$books = Book::withOnly('genre')->get();
```

### 约束预加载

有时你可能希望预加载某个关系，同时又为该预加载查询指定额外的查询条件。你可以通过向 `with` 方法传入一个关系数组来实现，其中**数组的键**是关系名称，**数组的值**是一个闭包，用于为预加载查询添加额外的约束条件：

```php
use App\Models\User;
use Illuminate\Contracts\Database\Eloquent\Builder;

$users = User::with(['posts' => function (Builder $query) {
    $query->where('title', 'like', '%code%');
}])->get();
```

在这个示例中，Eloquent 只会预加载 `title` 字段中包含 `code` 这个单词的文章。你还可以调用其他的 [查询构建器（query builder）](/docs/laravel/12.x/queries) 方法，以进一步自定义预加载操作：

```php
$users = User::with(['posts' => function (Builder $query) {
    $query->orderBy('created_at', 'desc');
}])->get();
```

#### 约束 `morphTo` 关系的预加载（

如果你正在预加载一个 `morphTo` 关系，Eloquent 将会执行**多条查询**来获取每一种类型的关联模型。你可以使用 `MorphTo` 关系的 `constrain` 方法，为这些查询分别添加额外的约束条件：

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



在这个示例中，Eloquent 只会预加载**未被隐藏的文章**，以及 `type` 字段值为 `"educational"` 的视频。

#### 结合关系存在性进行约束预加载

有时，你可能既需要**检查某个关系是否存在**，又需要在**相同条件下加载该关系**。例如，你可能希望只检索那些其子级 `Post` 模型满足特定查询条件的 `User` 模型，同时还要预加载这些符合条件的文章。

你可以使用 `withWhereHas` 方法来完成这一操作：

```php
use App\Models\User;

$users = User::withWhereHas('posts', function ($query) {
    $query->where('featured', true);
})->get();
```

### 延迟预加载

有时，你可能需要在父模型已经被检索之后再预加载某个关系。例如，当你需要**动态决定是否加载关联模型**时，这种方式会非常有用：

```php
use App\Models\Book;

$books = Book::all();

if ($someCondition) {
    $books->load('author', 'publisher');
}
```

如果你需要为预加载查询设置额外的查询约束条件，可以传入一个以关系名为键的数组。数组的值应当是闭包实例，这些闭包将接收查询实例：

```php
$author->load(['books' => function (Builder $query) {
    $query->orderBy('published_date', 'asc');
}]);
```

如果你只希望在关系**尚未被加载**的情况下才加载该关系，可以使用 `loadMissing` 方法：

```php
$book->loadMissing('author');
```

#### 嵌套延迟预加载与 `morphTo`

如果你希望预加载一个 `morphTo` 关系，同时还预加载该关系可能返回的各个实体上的嵌套关系，你可以使用 `loadMorph` 方法。



该方法将 `morphTo` 关系的名称作为**第一个参数**，并将一个由**模型 / 关系对**组成的数组作为**第二个参数**。
为了帮助说明该方法，我们来看下面这个模型示例：

```php
<?php

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class ActivityFeed extends Model
{
    /**
     * 获取活动动态记录的父模型
     */
    public function parentable(): MorphTo
    {
        return $this->morphTo();
    }
}
```

在这个示例中，假设 `Event`、`Photo` 和 `Post` 模型都可能创建 `ActivityFeed` 模型。此外，假设 `Event` 模型属于一个 `Calendar` 模型，`Photo` 模型与 `Tag` 模型相关联，而 `Post` 模型属于一个 `Author` 模型。

基于这些模型定义和关系，我们可以检索 `ActivityFeed` 模型实例，并预加载所有 `parentable` 模型及其各自对应的嵌套关系：

```php
$activities = ActivityFeed::with('parentable')
    ->get()
    ->loadMorph('parentable', [
        Event::class => ['calendar'],
        Photo::class => ['tags'],
        Post::class => ['author'],
    ]);
```

### 自动预加载

> [!警告]
> 该特性目前仍处于 Beta 阶段，用于收集社区反馈。即使在补丁版本（patch releases）中，该特性的行为和功能也可能发生变化。

在许多情况下，Laravel 可以自动预加载你所访问的关系。要启用自动预加载，你应当在应用的 `AppServiceProvider` 的 `boot` 方法中调用 `Model::automaticallyEagerLoadRelationships` 方法：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 引导任何应用服务
 */
public function boot(): void
{
    Model::automaticallyEagerLoadRelationships();
}
```

当该特性被启用后，Laravel 将尝试自动加载你所访问但尚未被加载的任何关系。例如，考虑下面的场景：

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



通常，上述代码会为每个用户执行一次查询以获取其文章（posts），并且还会为每一篇文章执行一次查询以获取其评论（comments）。然而，当启用了 `automaticallyEagerLoadRelationships` 功能后，Laravel 会在你尝试访问任意一个用户的 posts 时，自动对用户集合中的所有用户进行一次[延迟预加载](#lazy-eager-loading)。同样地，当你尝试访问任意一篇已检索文章的 comments 时，Laravel 也会为最初检索到的所有文章一次性延迟预加载它们的评论。

如果你不希望在全局范围内启用自动预加载关系，你仍然可以仅针对某一个 Eloquent 集合实例启用该功能，只需在集合上调用 `withRelationshipAutoloading` 方法即可：

```php
$users = User::where('vip', true)->get();

return $users->withRelationshipAutoloading();
```

### 禁止延迟加载

如前所述，**预加载（eager loading）关系**通常能够为应用带来显著的性能提升。因此，如果你有需要，可以指示 Laravel **始终禁止关系的延迟加载（lazy loading）**。
要实现这一点，可以调用 Eloquent 基础模型类所提供的 `preventLazyLoading` 方法。通常建议在应用的 `AppServiceProvider` 类的 `boot` 方法中调用该方法。

`preventLazyLoading` 方法接收一个**可选的布尔参数**，用于指示是否应当禁止延迟加载。例如，你可能只希望在**非生产环境**中禁用延迟加载，这样即使生产环境的代码中不小心存在延迟加载的关系，应用仍然可以正常运行，而不会直接报错：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 引导（初始化）任何应用服务
 */
public function boot(): void
{
    Model::preventLazyLoading(! $this->app->isProduction());
}
```



在禁止延迟加载之后，当你的应用尝试对任何 Eloquent 关系进行延迟加载时，Eloquent 将会抛出 `Illuminate\Database\LazyLoadingViolationException` 异常。

你可以通过 `handleLazyLoadingViolationsUsing` 方法来自定义延迟加载违规时的处理行为。例如，使用该方法，你可以指示在发生延迟加载违规时**仅记录日志**，而不是通过抛出异常来中断应用的执行：

```php
Model::handleLazyLoadingViolationUsing(function (Model $model, string $relation) {
    $class = $model::class;

    info("Attempted to lazy load [{$relation}] on model [{$class}].");
});
```

## 插入与更新关联模型

### `save` 方法

Eloquent 提供了便捷的方法，用于向关系中添加新的模型。例如，假设你需要为一篇文章添加一条新的评论。与其在 `Comment` 模型上手动设置 `post_id` 属性，不如使用关系的 `save` 方法来插入该评论：

```php
use App\Models\Comment;
use App\Models\Post;

$comment = new Comment(['message' => 'A new comment.']);

$post = Post::find(1);

$post->comments()->save($comment);
```

请注意，我们并没有以动态属性的方式访问 `comments` 关系。相反，我们是调用了 `comments` 方法来获取关系实例。`save` 方法会自动为新的 `Comment` 模型填充正确的 `post_id` 值。

如果你需要保存多个关联模型，可以使用 `saveMany` 方法：

```php
$post = Post::find(1);

$post->comments()->saveMany([
    new Comment(['message' => 'A new comment.']),
    new Comment(['message' => 'Another new comment.']),
]);
```

`save` 与 `saveMany` 方法会将给定的模型实例持久化到数据库中，但**不会**将新持久化的模型自动添加到父模型中已经加载到内存的关系集合中。如果你打算在调用 `save` 或 `saveMany` 方法之后继续访问该关系，可能需要使用 `refresh` 方法重新加载模型及其关系：

```php
$post->comments()->save($comment);

$post->refresh();

// 所有评论，包括刚刚保存的新评论……
$post->comments;
```



#### 递归保存模型及其关系

如果你希望**保存（save）模型及其所有关联关系**，可以使用 `push` 方法。在这个示例中，`Post` 模型将会被保存，同时其评论（comments）以及评论的作者（author）也会被保存：

```php
$post = Post::find(1);

$post->comments[0]->message = 'Message';
$post->comments[0]->author->name = 'Author Name';

$post->push();
```

`pushQuietly` 方法可用于保存模型及其关联关系，同时**不触发任何事件**：

```php
$post->pushQuietly();
```

### `create` 方法

除了 `save` 和 `saveMany` 方法之外，你还可以使用 `create` 方法，它接受一个属性数组，创建模型并将其插入数据库。`save` 与 `create` 的区别在于：`save` 接受一个完整的 Eloquent 模型实例，而 `create` 接受一个普通 PHP `array`。`create` 方法会返回新创建的模型实例：

```php
use App\Models\Post;

$post = Post::find(1);

$comment = $post->comments()->create([
    'message' => 'A new comment.',
]);
```

你可以使用 `createMany` 方法来创建多个关联模型：

```php
$post = Post::find(1);

$post->comments()->createMany([
    ['message' => 'A new comment.'],
    ['message' => 'Another new comment.'],
]);
```

`createQuietly` 和 `createManyQuietly` 方法可用于**创建模型而不触发任何事件**：

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

你还可以使用 `findOrNew`、`firstOrNew`、`firstOrCreate` 和 `updateOrCreate` 方法来[在关系上创建或更新模型](/docs/laravel/12.x/eloquent#upserts)。

> [!注意]
> 在使用 `create` 方法之前，请务必查看 [批量赋值（mass assignment）](/docs/laravel/12.x/eloquent#mass-assignment) 文档。


<a name="updating-belongs-to-relationships"></a>
### 属于关系

如果想将子模型分配给新的父模型，可以使用 `associate` 方法。在这个例子中，`User` 模型定义了一个到 `Account` 模型的 `belongsTo` 关系。`associate` 方法将在子模型上设置外键：

```php
use App\Models\Account;

$account = Account::find(10);

$user->account()->associate($account);

$user->save();
```

要从子模型中移除父模型，可以使用 `dissociate` 方法。该方法将关系的外键设置为 `null`：

```php
$user->account()->dissociate();

$user->save();
```

<a name="updating-many-to-many-relationships"></a>
### 多对多关系

<a name="attaching-detaching"></a>
#### 附加 / 分离

Eloquent 还提供了一些方法，使得处理多对多关系更加方便。例如，假设一个用户可以拥有多个角色，而一个角色也可以拥有多个用户。你可以使用 `attach` 方法将一个角色附加到一个用户，通过在关系的中间表中插入一条记录：

```php
use App\Models\User;

$user = User::find(1);

$user->roles()->attach($roleId);
```

当向模型附加关系时，你也可以传递一个包含要插入到中间表的附加数据的数组：

```php
$user->roles()->attach($roleId, ['expires' => $expires]);
```

有时需要从用户中移除一个角色。要移除多对多关系记录，可以使用 `detach` 方法。`detach` 方法将从中间表中删除适当的记录；但是，两个模型将仍然保留在数据库中：

```php
// 从用户中分离单个角色...
$user->roles()->detach($roleId);

// 从用户中分离所有角色...
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

你也可以传递附加的中间表值与 ID：

```php
$user->roles()->sync([1 => ['expires' => true], 2, 3]);
```

如果希望将相同的中间表值与每个同步模型 ID 一起插入，可以使用 `syncWithPivotValues` 方法：

```php
$user->roles()->syncWithPivotValues([1, 2, 3], ['active' => true]);
```

如果不想分离缺少在给定数组中的现有 ID，可以使用 `syncWithoutDetaching` 方法：

```php
$user->roles()->syncWithoutDetaching([1, 2, 3]);
```

<a name="toggling-associations"></a>
#### 切换关联

多对多关系还提供了一个 `toggle` 方法，用于「切换」给定相关模型的附加状态。如果给定的 ID 当前已附加，它将被分离。同样，如果它当前处于分离状态，它将被附加：

```php
$user->roles()->toggle([1, 2, 3]);
```

你也可以传递附加表的额外中间值与 ID：

```php
$user->roles()->toggle([
    1 => ['expires' => true],
    2 => ['expires' => true],
]);
```

<a name="updating-a-record-on-the-intermediate-table"></a>
#### 更新中间表上的记录



如果你需要更新关系的中间表中的现有行，你可以使用 `updateExistingPivot` 方法。该方法接受中间记录外键和要更新的属性数组：

```php
$user = User::find(1);

$user->roles()->updateExistingPivot($roleId, [
    'active' => false,
]);
```

<a name="touching-parent-timestamps"></a>
## 更新父级时间戳

当一个模型定义了一个 `belongsTo` 或 `belongsToMany` 关系到另一个模型，比如一个 `Comment` 属于一个 `Post`，有时在更新子模型时更新父模型的时间戳是有帮助的。

例如，当一个 `Comment` 模型被更新时，你可能希望自动「触摸」拥有的 `Post` 的 `updated_at` 时间戳，使其设置为当前日期和时间。为了实现这一点，你可以在子模型中添加一个 `touches` 属性，其中包含应在更新子模型时更新其 `updated_at` 时间戳的关系名称：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Comment extends Model
{
    /**
     * 所有要被触摸的关系。
     *
     * @var array
     */
    protected $touches = ['post'];

    /**
     * 获取评论所属的帖子。
     */
    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }
}
```

> 警告
> 只有当子模型使用 Eloquent 的 `save` 方法进行更新时，父模型的时间戳才会被更新。
