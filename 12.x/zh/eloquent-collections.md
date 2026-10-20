
# Eloquent：集合

-   [介绍](#introduction)
-   [可用方法](#available-methods)
-   [自定义集合](#custom-collections)

## 介绍

所有返回多个模型结果的 Eloquent 方法都会返回 `Illuminate\Database\Eloquent\Collection` 类的实例，包括通过 `get` 方法检索的结果或通过关联访问的结果。
Eloquent 集合对象扩展了 Laravel 的 [基础集合](/docs/laravel/12.x/collections)，因此它自然继承了数十个用于流畅操作 Eloquent 模型底层数组的方法。
务必查看 Laravel 集合文档，以了解这些有用方法的全部内容！

所有集合也可以作为迭代器使用，允许你像操作普通 PHP 数组一样循环访问它们：

```php
use App\Models\User;

$users = User::where('active', 1)->get();

foreach ($users as $user) {
    echo $user->name;
}
```

然而，如前所述，集合比数组更强大，并且提供了各种 map / reduce 操作，可以通过直观的接口进行链式调用。
例如，我们可以移除所有非激活模型，然后收集每个剩余用户的名字：

```php
$names = User::all()->reject(function (User $user) {
    return $user->active === false;
})->map(function (User $user) {
    return $user->name;
});
```

#### Eloquent 集合转换

虽然大多数 Eloquent 集合方法会返回新的 Eloquent 集合实例，
但 `collapse`、`flatten`、`flip`、`keys`、`pluck` 和 `zip` 方法会返回 [基础集合](/docs/laravel/12.x/collections) 实例。
同样地，如果 `map` 操作返回的集合不包含任何 Eloquent 模型，它将被转换为基础集合实例。



## 可用方法

所有 Eloquent 集合都扩展了基础 [Laravel 集合](/docs/laravel/12.x/collections#available-methods) 对象；
因此，它们继承了基础集合类提供的所有强大方法。

此外，`Illuminate\Database\Eloquent\Collection` 类提供了方法超集，用于帮助管理你的模型集合。
大多数方法返回 `Illuminate\Database\Eloquent\Collection` 实例；
然而，一些方法，如 `modelKeys`，会返回 `Illuminate\Support\Collection` 实例。

<style>
    .collection-method-list > p {
        columns: 14.4em 1; -moz-columns: 14.4em 1; -webkit-columns: 14.4em 1;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .collection-method code {
        font-size: 14px;
    }

    .collection-method:not(.first-collection-method) {
        margin-top: 50px;
    }
</style>

<div class="collection-method-list" markdown="1">

[append](#method-append)
[contains](#method-contains)
[diff](#method-diff)
[except](#method-except)
[find](#method-find)
[findOrFail](#method-find-or-fail)
[fresh](#method-fresh)
[intersect](#method-intersect)
[load](#method-load)
[loadMissing](#method-loadMissing)
[modelKeys](#method-modelKeys)
[makeVisible](#method-makeVisible)
[makeHidden](#method-makeHidden)
[only](#method-only)
[partition](#method-partition)
[setVisible](#method-setVisible)
[setHidden](#method-setHidden)
[toQuery](#method-toquery)
[unique](#method-unique)

</div>

#### `append($attributes)` {.collection-method .first-collection-method}

`append` 方法可用于指示某个属性应为集合中的每个模型 [追加](/docs/laravel/12.x/eloquent-serialization#appending-values-to-json)。
此方法接受一个属性数组或单个属性：

```php
$users->append('team');

$users->append(['team', 'is_admin']);
```

#### `contains($key, $operator = null, $value = null)` {.collection-method}

`contains` 方法可用于判断集合中是否包含给定的模型实例。
此方法接受一个主键或一个模型实例：

```php
$users->contains(1);

$users->contains(User::find(1));
```

#### `diff($items)` {.collection-method}

`diff` 方法返回给定集合中不存在的所有模型：

```php
use App\Models\User;

$users = $users->diff(User::whereIn('id', [1, 2, 3])->get());
```



#### `except($keys)` {.collection-method}

`except` 方法返回所有不具有给定主键的模型：

```php
$users = $users->except([1, 2, 3]);
```

#### `find($key)` {.collection-method}

`find` 方法返回具有与给定键匹配的主键的模型。
如果 `$key` 是一个模型实例，`find` 将尝试返回与该主键匹配的模型。
如果 `$key` 是一个键数组，`find` 将返回所有主键在给定数组中的模型：

```php
$users = User::all();

$user = $users->find(1);
```

#### `findOrFail($key)` {.collection-method}

`findOrFail` 方法返回具有与给定键匹配的主键的模型，
如果在集合中找不到匹配的模型，则抛出 `Illuminate\Database\Eloquent\ModelNotFoundException` 异常：

```php
$users = User::all();

$user = $users->findOrFail(1);
```

#### `fresh($with = [])` {.collection-method}

`fresh` 方法从数据库中检索集合中每个模型的新实例。
此外，任何指定的关系将被预加载：

```php
$users = $users->fresh();

$users = $users->fresh('comments');
```

#### `intersect($items)` {.collection-method}

`intersect` 方法返回在给定集合中也存在的所有模型：

```php
use App\Models\User;

$users = $users->intersect(User::whereIn('id', [1, 2, 3])->get());
```

#### `load($relations)` {.collection-method}

`load` 方法对集合中的所有模型预加载给定的关系：

```php
$users->load(['comments', 'posts']);

$users->load('comments.author');

$users->load(['comments', 'posts' => fn ($query) => $query->where('active', 1)]);
```



#### `loadMissing($relations)` {.collection-method}

`loadMissing` 方法会为集合中所有模型预加载给定的关系，如果这些关系尚未被加载：

```php
$users->loadMissing(['comments', 'posts']);

$users->loadMissing('comments.author');

$users->loadMissing(['comments', 'posts' => fn ($query) => $query->where('active', 1)]);
```

#### `modelKeys()` {.collection-method}

`modelKeys` 方法返回集合中所有模型的主键：

```php
$users->modelKeys();

// [1, 2, 3, 4, 5]
```

#### `makeVisible($attributes)` {.collection-method}

`makeVisible` 方法将通常在集合中每个模型上被“隐藏”的属性 [设为可见](/docs/laravel/12.x/eloquent-serialization#hiding-attributes-from-json)：

```php
$users = $users->makeVisible(['address', 'phone_number']);
```

#### `makeHidden($attributes)` {.collection-method}

`makeHidden` 方法将通常在集合中每个模型上被“可见”的属性 [隐藏](/docs/laravel/12.x/eloquent-serialization#hiding-attributes-from-json)：

```php
$users = $users->makeHidden(['address', 'phone_number']);
```

#### `only($keys)` {.collection-method}

`only` 方法返回所有具有给定主键的模型：

```php
$users = $users->only([1, 2, 3]);
```

#### `partition` {.collection-method}

`partition` 方法返回一个 `Illuminate\Support\Collection` 实例，该实例包含 `Illuminate\Database\Eloquent\Collection` 集合实例：

```php
$partition = $users->partition(fn ($user) => $user->age > 18);

dump($partition::class);    // Illuminate\Support\Collection
dump($partition[0]::class); // Illuminate\Database\Eloquent\Collection
dump($partition[1]::class); // Illuminate\Database\Eloquent\Collection
```

#### `setVisible($attributes)` {.collection-method}

`setVisible` 方法 [临时覆盖](/docs/laravel/12.x/eloquent-serialization#temporarily-modifying-attribute-visibility)集合中每个模型的所有可见属性：

```php
$users = $users->setVisible(['id', 'name']);
```

#### `setHidden($attributes)` {.collection-method}



`setHidden` 方法 [临时覆盖](/docs/laravel/12.x/eloquent-serialization#temporarily-modifying-attribute-visibility)集合中每个模型的所有隐藏属性：

```php
$users = $users->setHidden(['email', 'password', 'remember_token']);
```

#### `toQuery()` {.collection-method}

`toQuery` 方法返回一个 Eloquent 查询构建器实例，其中包含集合模型主键的 `whereIn` 约束：

```php
use App\Models\User;

$users = User::where('status', 'VIP')->get();

$users->toQuery()->update([
    'status' => 'Administrator',
]);
```

#### `unique($key = null, $strict = false)` {.collection-method}

`unique` 方法返回集合中所有唯一的模型。
集合中任何与另一个模型主键相同的模型都会被移除：

```php
$users = $users->unique();
```
## 自定义集合

如果你希望在与某个模型交互时使用自定义 `Collection` 对象，可以在模型上添加 `CollectedBy` 属性：

```php
<?php

namespace App\Models;

use App\Support\UserCollection;
use Illuminate\Database\Eloquent\Attributes\CollectedBy;
use Illuminate\Database\Eloquent\Model;

#[CollectedBy(UserCollection::class)]
class User extends Model
{
    // ...
}
```

或者，你可以在模型上定义一个 `newCollection` 方法：

```php
<?php

namespace App\Models;

use App\Support\UserCollection;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 创建一个新的 Eloquent 集合实例。
     *
     * @param  array<int, \Illuminate\Database\Eloquent\Model>  $models
     * @return \Illuminate\Database\Eloquent\Collection<int, \Illuminate\Database\Eloquent\Model>
     */
    public function newCollection(array $models = []): Collection
    {
        return new UserCollection($models);
    }
}
```
一旦你定义了 `newCollection` 方法或在模型上添加了 `CollectedBy` 属性，
每当 Eloquent 通常返回 `Illuminate\Database\Eloquent\Collection` 实例时，你将收到自定义集合实例。

如果你希望在应用中的每个模型都使用自定义集合，
应在一个基础模型类上定义 `newCollection` 方法，该基础类由应用中所有模型继承。
