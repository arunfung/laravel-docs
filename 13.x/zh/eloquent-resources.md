# Eloquent: API 资源

- [介绍](#introduction)
- [生成资源](#generating-resources)
- [概念概述](#concept-overview)
    - [资源集合](#resource-collections)
- [编写资源](#writing-resources)
    - [数据包裹](#data-wrapping)
    - [分页](#pagination)
    - [条件属性](#conditional-attributes)
    - [条件关联](#conditional-relationships)
    - [添加元数据](#adding-meta-data)
- [JSON:API 资源](#jsonapi-resources)
    - [生成 JSON:API 资源](#generating-jsonapi-resources)
    - [定义属性](#defining-jsonapi-attributes)
    - [定义关联](#defining-jsonapi-relationships)
    - [资源类型与 ID](#jsonapi-resource-type-and-id)
    - [稀疏字段集与关联包含](#jsonapi-sparse-fieldsets-and-includes)
    - [链接与元数据](#jsonapi-links-and-meta)
- [资源响应](#resource-responses)

<a name="introduction"></a>
## 介绍

构建 API 时，你可能需要在 Eloquent 模型与实际返回给应用用户的 JSON 响应之间设置一个转换层。例如，你可能希望仅向部分用户显示某些属性，或始终在模型的 JSON 表示中包含某些关联。Eloquent 资源类让你能够以简洁、直观的方式，将模型及模型集合转换为 JSON。

当然，你始终可以使用 Eloquent 模型或集合的 `toJson` 方法将它们转换为 JSON；不过，Eloquent 资源能让你更精细、更灵活地控制模型及其关联的 JSON 序列化。

<a name="generating-resources"></a>
## 生成资源

你可以使用 `make:resource` Artisan 命令生成资源类。默认情况下，资源会放在应用的 `app/Http/Resources` 目录中。资源类继承自 `Illuminate\Http\Resources\Json\JsonResource` 类：

```shell
php artisan make:resource UserResource
```

<a name="generating-resource-collections"></a>
#### 资源集合

除了生成转换单个模型的资源外，你还可以生成负责转换模型集合的资源。这让 JSON 响应能够包含与整个资源集合相关的链接及其他元信息。

要创建资源集合，可以在生成资源时使用 `--collection` 选项。或者，在资源名称中包含 `Collection`，也会让 Laravel 创建资源集合。资源集合继承自 `Illuminate\Http\Resources\Json\ResourceCollection` 类：

```shell
php artisan make:resource User --collection

php artisan make:resource UserCollection
```

<a name="concept-overview"></a>
## 概念概述

> [!NOTE]
> 这里概括介绍资源和资源集合。强烈建议你继续阅读本文的其他章节，以深入了解资源提供的自定义能力和各项功能。

在深入探讨编写资源时的所有可用选项之前，我们先从整体上了解资源在 Laravel 中的使用方式。资源类表示需要转换为 JSON 结构的单个模型。例如，下面是一个简单的 `UserResource` 资源类：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    /**
     * 将资源转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'created_at' => $this->created_at,
            'updated_at' => $this->updated_at,
        ];
    }
}
```

每个资源类都定义了一个 `toArray` 方法，返回一个属性数组。当资源作为路由或控制器方法的响应返回时，这些属性会被转换为 JSON。

注意，我们可以直接通过 `$this` 变量访问模型属性。这是因为资源类会自动将属性和方法的访问代理到底层模型，方便你使用。定义好资源后，就可以从路由或控制器返回它。资源通过构造函数接收底层模型实例：

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return new UserResource(User::findOrFail($id));
});
```

为方便起见，你可以使用模型的 `toResource` 方法，它会遵循框架约定，自动查找模型对应的资源：

```php
return User::findOrFail($id)->toResource();
```

调用 `toResource` 方法时，Laravel 会在最接近模型命名空间的 `Http\Resources` 命名空间中，尝试查找与模型同名、可选地以 `Resource` 为后缀的资源。

如果资源类不遵循这一命名约定，或位于其他命名空间，你可以使用 `UseResource` 特性指定模型的默认资源：

```php
<?php

namespace App\Models;

use App\Http\Resources\CustomUserResource;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Attributes\UseResource;

#[UseResource(CustomUserResource::class)]
class User extends Model
{
    // ...
}
```

你也可以将资源类传给 `toResource` 方法来指定资源类：

```php
return User::findOrFail($id)->toResource(CustomUserResource::class);
```

<a name="resource-collections"></a>
### 资源集合

如果要返回资源集合或分页响应，你应该在路由或控制器中创建资源实例时，使用资源类提供的 `collection` 方法：

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/users', function () {
    return UserResource::collection(User::all());
});
```

或者，为方便起见，你可以使用 Eloquent 集合的 `toResourceCollection` 方法，它会遵循框架约定，自动查找模型对应的资源集合：

```php
return User::all()->toResourceCollection();
```

调用 `toResourceCollection` 方法时，Laravel 会在最接近模型命名空间的 `Http\Resources` 命名空间中，尝试查找与模型同名、以 `Collection` 为后缀的资源集合。

如果资源集合类不遵循这一命名约定，或位于其他命名空间，你可以使用 `UseResourceCollection` 特性指定模型的默认资源集合：

```php
<?php

namespace App\Models;

use App\Http\Resources\CustomUserCollection;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Attributes\UseResourceCollection;

#[UseResourceCollection(CustomUserCollection::class)]
class User extends Model
{
    // ...
}
```

你也可以将资源集合类传给 `toResourceCollection` 方法来指定资源集合类：

```php
return User::all()->toResourceCollection(CustomUserCollection::class);
```

<a name="custom-resource-collections"></a>
#### 自定义资源集合

默认情况下，资源集合不允许添加需要随集合一同返回的自定义元数据。如果你想自定义资源集合响应，可以创建一个专门的资源来表示该集合：

```shell
php artisan make:resource UserCollection
```

生成资源集合类后，你就可以轻松定义响应中应包含的元数据：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    /**
     * 将资源集合转换为数组。
     *
     * @return array<int|string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'data' => $this->collection,
            'links' => [
                'self' => 'link-value',
            ],
        ];
    }
}
```

定义好资源集合后，就可以从路由或控制器返回它：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::all());
});
```

或者，为方便起见，你可以使用 Eloquent 集合的 `toResourceCollection` 方法，它会遵循框架约定，自动查找模型对应的资源集合：

```php
return User::all()->toResourceCollection();
```

调用 `toResourceCollection` 方法时，Laravel 会在最接近模型命名空间的 `Http\Resources` 命名空间中，尝试查找与模型同名、以 `Collection` 为后缀的资源集合。

<a name="preserving-collection-keys"></a>
#### 保留集合键

从路由返回资源集合时，Laravel 会重置集合的键，使其按数字顺序排列。不过，你可以在资源类上使用 `PreserveKeys` 特性，指示应保留集合的原始键：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Attributes\PreserveKeys;
use Illuminate\Http\Resources\Json\JsonResource;

#[PreserveKeys]
class UserResource extends JsonResource
{
    // ...
}
```

当 `preserveKeys` 属性设置为 `true` 时，从路由或控制器返回集合时，集合的键将被保留：

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/users', function () {
    return UserResource::collection(User::all()->keyBy->id);
});
```

<a name="customizing-the-underlying-resource-class"></a>
#### 自定义底层资源类

通常，资源集合的 `$this->collection` 属性会自动填充为将集合中每一项映射到其单个资源类后的结果。单个资源类的名称默认为集合类名去掉末尾的 `Collection` 部分。此外，你可以根据个人偏好，为单个资源类添加或省略 `Resource` 后缀。

例如，`UserCollection` 会尝试将给定的用户实例映射为 `UserResource` 资源。要自定义这一行为，可以在资源集合上使用 `Collects` 特性：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Attributes\Collects;
use Illuminate\Http\Resources\Json\ResourceCollection;

#[Collects(Member::class)]
class UserCollection extends ResourceCollection
{
    // ...
}
```

<a name="writing-resources"></a>
## 编写资源

> [!NOTE]
> 如果你尚未阅读[概念概述](#concept-overview)，强烈建议先阅读该部分，再继续阅读本文。

资源只需将给定模型转换为数组。因此，每个资源都包含一个 `toArray` 方法，将模型属性转换为适合 API 的数组，以便从应用的路由或控制器返回：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    /**
     * 将资源转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'created_at' => $this->created_at,
            'updated_at' => $this->updated_at,
        ];
    }
}
```

定义好资源后，就可以直接从路由或控制器返回它：

```php
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return User::findOrFail($id)->toResource();
});
```

<a name="relationships"></a>
#### 关联

如果希望在响应中包含关联资源，可以将它们添加到资源的 `toArray` 方法返回的数组中。在本例中，我们会使用 `PostResource` 资源的 `collection` 方法，将用户的博客文章添加到资源响应中：

```php
use App\Http\Resources\PostResource;
use Illuminate\Http\Request;

/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        'posts' => PostResource::collection($this->posts),
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

> [!NOTE]
> 如果你希望仅在关联已加载时才包含它们，请参阅[条件关联](#conditional-relationships)文档。

<a name="writing-resource-collections"></a>
#### 资源集合

资源将单个模型转换为数组，而资源集合将模型集合转换为数组。不过，你并不一定要为每个模型都定义资源集合类，因为所有 Eloquent 模型集合都提供了 `toResourceCollection` 方法，可以即时生成一个临时资源集合：

```php
use App\Models\User;

Route::get('/users', function () {
    return User::all()->toResourceCollection();
});
```

不过，如果需要自定义随集合返回的元数据，就必须定义自己的资源集合：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    /**
     * 将资源集合转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'data' => $this->collection,
            'links' => [
                'self' => 'link-value',
            ],
        ];
    }
}
```

与单个资源一样，资源集合也可以直接从路由或控制器返回：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::all());
});
```

或者，为方便起见，你可以使用 Eloquent 集合的 `toResourceCollection` 方法，它会遵循框架约定，自动查找模型对应的资源集合：

```php
return User::all()->toResourceCollection();
```

调用 `toResourceCollection` 方法时，Laravel 会在最接近模型命名空间的 `Http\Resources` 命名空间中，尝试查找与模型同名、以 `Collection` 为后缀的资源集合。

<a name="data-wrapping"></a>
### 数据包裹

默认情况下，将资源响应转换为 JSON 时，最外层资源会被包裹在 `data` 键中。例如，典型的资源集合响应如下：

```json
{
    "data": [
        {
            "id": 1,
            "name": "Eladio Schroeder Sr.",
            "email": "therese28@example.com"
        },
        {
            "id": 2,
            "name": "Liliana Mayert",
            "email": "evandervort@example.com"
        }
    ]
}
```

如果想禁用最外层资源的数据包裹，你应该在基类 `Illuminate\Http\Resources\Json\JsonResource` 上调用 `withoutWrapping` 方法。通常，你应该在 `AppServiceProvider` 或应用每次请求都会加载的其他[服务提供者](/docs/{{version}}/providers)中调用该方法：

```php
<?php

namespace App\Providers;

use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 引导应用服务。
     */
    public function boot(): void
    {
        JsonResource::withoutWrapping();
    }
}
```

> [!WARNING]
> `withoutWrapping` 方法只影响最外层响应，不会移除你在自定义资源集合中手动添加的 `data` 键。

<a name="wrapping-nested-resources"></a>
#### 包裹嵌套资源

你可以自由决定资源关联的数据包裹方式。如果希望所有资源集合无论嵌套层级如何，都被包裹在 `data` 键中，你应该为每个资源定义资源集合类，并将集合放在 `data` 键中返回。

你可能会担心，这是否会让最外层资源被包裹在两层 `data` 键中。不必担心，Laravel 绝不会让资源被意外地重复包裹，因此你无需考虑正在转换的资源集合的嵌套层级：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\ResourceCollection;

class CommentsCollection extends ResourceCollection
{
    /**
     * 将资源集合转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return ['data' => $this->collection];
    }
}
```

<a name="data-wrapping-and-pagination"></a>
#### 数据包裹与分页

通过资源响应返回分页集合时，即使已经调用了 `withoutWrapping` 方法，Laravel 仍会将资源数据包裹在 `data` 键中。这是因为分页响应始终包含 `meta` 和 `links` 键，用于提供分页器的状态信息：

```json
{
    "data": [
        {
            "id": 1,
            "name": "Eladio Schroeder Sr.",
            "email": "therese28@example.com"
        },
        {
            "id": 2,
            "name": "Liliana Mayert",
            "email": "evandervort@example.com"
        }
    ],
    "links":{
        "first": "http://example.com/users?page=1",
        "last": "http://example.com/users?page=1",
        "prev": null,
        "next": null
    },
    "meta":{
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "http://example.com/users",
        "per_page": 15,
        "to": 10,
        "total": 10
    }
}
```

<a name="pagination"></a>
### 分页

你可以将 Laravel 分页器实例传给资源的 `collection` 方法，或传给自定义资源集合：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::paginate());
});
```

或者，为方便起见，你可以使用分页器的 `toResourceCollection` 方法，它会遵循框架约定，自动查找分页模型对应的资源集合：

```php
return User::paginate()->toResourceCollection();
```

分页响应始终包含 `meta` 和 `links` 键，用于提供分页器的状态信息：

```json
{
    "data": [
        {
            "id": 1,
            "name": "Eladio Schroeder Sr.",
            "email": "therese28@example.com"
        },
        {
            "id": 2,
            "name": "Liliana Mayert",
            "email": "evandervort@example.com"
        }
    ],
    "links":{
        "first": "http://example.com/users?page=1",
        "last": "http://example.com/users?page=1",
        "prev": null,
        "next": null
    },
    "meta":{
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "http://example.com/users",
        "per_page": 15,
        "to": 10,
        "total": 10
    }
}
```

<a name="customizing-the-pagination-information"></a>
#### 自定义分页信息

如果想自定义分页响应的 `links` 或 `meta` 键中的信息，你可以在资源上定义 `paginationInformation` 方法。该方法会接收 `$paginated` 数据和默认信息数组 `$default`，后者是一个包含 `links` 和 `meta` 键的数组：

```php
/**
 * 自定义资源的分页信息。
 *
 * @param  \Illuminate\Http\Request  $request
 * @param  array  $paginated
 * @param  array  $default
 * @return array
 */
public function paginationInformation($request, $paginated, $default)
{
    $default['links']['custom'] = 'https://example.com';

    return $default;
}
```

<a name="conditional-attributes"></a>
### 条件属性

有时，你可能希望仅在满足给定条件时，才将某个属性包含在资源响应中。例如，你可能希望仅在当前用户是「管理员」时才包含某个值。Laravel 提供了多种辅助方法来处理这类情况。你可以使用 `when` 方法，有条件地将属性添加到资源响应中：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        'secret' => $this->when($request->user()->isAdmin(), 'secret-value'),
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

在本例中，只有当已认证用户的 `isAdmin` 方法返回 `true` 时，`secret` 键才会出现在最终的资源响应中。如果该方法返回 `false`，`secret` 键就会在资源响应发送给客户端之前被移除。`when` 方法让你能够简洁地定义资源，而无需在构建数组时使用条件语句。

`when` 方法还接受闭包作为第二个参数，这样只有当给定条件为 `true` 时，才会计算结果值：

```php
'secret' => $this->when($request->user()->isAdmin(), function () {
    return 'secret-value';
}),
```

`whenHas` 方法可以在底层模型确实存在某个属性时，才包含该属性：

```php
'name' => $this->whenHas('name'),
```

此外，`whenNotNull` 方法可以在属性不为 null 时，才将该属性包含在资源响应中：

```php
'name' => $this->whenNotNull($this->name),
```

<a name="merging-conditional-attributes"></a>
#### 合并条件属性

有时，你可能希望多个属性都仅在同一个条件满足时才包含在资源响应中。这时，可以使用 `mergeWhen` 方法，仅在给定条件为 `true` 时，才将这些属性包含在响应中：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        $this->mergeWhen($request->user()->isAdmin(), [
            'first-secret' => 'value',
            'second-secret' => 'value',
        ]),
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

同样，如果给定条件为 `false`，这些属性就会在资源响应发送给客户端之前被移除。

> [!WARNING]
> `mergeWhen` 方法不应在混用字符串键和数字键的数组中使用，也不应在数字键未按顺序排列的数组中使用。

<a name="conditional-relationships"></a>
### 条件关联

除了有条件地加载属性外，你还可以根据模型是否已加载某个关联，有条件地将该关联包含在资源响应中。这样，控制器就能决定要在模型上加载哪些关联，而资源则可以轻松地仅包含已经加载的关联。这有助于在资源中避免「N+1」查询问题。

`whenLoaded` 方法可用于有条件地加载关联。为避免不必要的关联加载，该方法接受关联名称，而不是关联本身：

```php
use App\Http\Resources\PostResource;

/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        'posts' => PostResource::collection($this->whenLoaded('posts')),
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

在本例中，如果关联尚未加载，`posts` 键就会在资源响应发送给客户端之前被移除。

<a name="conditional-relationship-counts"></a>
#### 条件关联数量

除了有条件地包含关联外，你还可以根据模型是否已加载关联数量，有条件地将关联「数量」包含在资源响应中：

```php
new UserResource($user->loadCount('posts'));
```

`whenCounted` 方法可以有条件地将关联数量包含在资源响应中。如果关联数量不存在，该方法会避免将这一属性包含在响应中：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'email' => $this->email,
        'posts_count' => $this->whenCounted('posts'),
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

在本例中，如果尚未加载 `posts` 关联的数量，`posts_count` 键就会在资源响应发送给客户端之前被移除。

其他类型的聚合结果，如 `avg`、`sum`、`min` 和 `max`，也可以通过 `whenAggregated` 方法有条件地加载：

```php
'words_avg' => $this->whenAggregated('posts', 'words', 'avg'),
'words_sum' => $this->whenAggregated('posts', 'words', 'sum'),
'words_min' => $this->whenAggregated('posts', 'words', 'min'),
'words_max' => $this->whenAggregated('posts', 'words', 'max'),
```

<a name="conditional-pivot-information"></a>
#### 条件中间表信息

除了有条件地在资源响应中包含关联信息外，你还可以使用 `whenPivotLoaded` 方法，有条件地包含多对多关联中间表的数据。`whenPivotLoaded` 方法的第一个参数是中间表名称。第二个参数应该是一个闭包，用于在模型上存在中间表信息时，返回需要包含的值：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'expires_at' => $this->whenPivotLoaded('role_user', function () {
            return $this->pivot->expires_at;
        }),
    ];
}
```

如果关联使用了[自定义中间表模型](/docs/{{version}}/eloquent-relationships#defining-custom-intermediate-table-models)，你可以将中间表模型实例作为第一个参数传给 `whenPivotLoaded` 方法：

```php
'expires_at' => $this->whenPivotLoaded(new Membership, function () {
    return $this->pivot->expires_at;
}),
```

如果中间表使用了 `pivot` 以外的访问器，你可以使用 `whenPivotLoadedAs` 方法：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'name' => $this->name,
        'expires_at' => $this->whenPivotLoadedAs('subscription', 'role_user', function () {
            return $this->subscription->expires_at;
        }),
    ];
}
```

<a name="adding-meta-data"></a>
### 添加元数据

某些 JSON API 标准要求在资源和资源集合响应中添加元数据。这通常包括指向资源或关联资源的 `links`，或关于资源本身的元数据。如果需要为资源返回附加元数据，可以将其包含在 `toArray` 方法中。例如，转换资源集合时，你可以包含 `links` 信息：

```php
/**
 * 将资源转换为数组。
 *
 * @return array<string, mixed>
 */
public function toArray(Request $request): array
{
    return [
        'data' => $this->collection,
        'links' => [
            'self' => 'link-value',
        ],
    ];
}
```

从资源返回附加元数据时，你无需担心会意外覆盖 Laravel 在返回分页响应时自动添加的 `links` 或 `meta` 键。你定义的任何附加 `links` 都会与分页器提供的链接合并。

<a name="top-level-meta-data"></a>
#### 顶层元数据

有时，你可能希望仅在资源是所返回的最外层资源时，才包含某些元数据。这通常是关于整个响应的元信息。要定义这些元数据，可以向资源类添加 `with` 方法。该方法应该返回一个元数据数组，只有当资源是正在转换的最外层资源时，才会将这些元数据包含在资源响应中：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    /**
     * 将资源集合转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return parent::toArray($request);
    }

    /**
     * 获取应随资源数组返回的附加数据。
     *
     * @return array<string, mixed>
     */
    public function with(Request $request): array
    {
        return [
            'meta' => [
                'key' => 'value',
            ],
        ];
    }
}
```

<a name="adding-meta-data-when-constructing-resources"></a>
#### 构建资源时添加元数据

你也可以在路由或控制器中构建资源实例时添加顶层数据。所有资源都提供了 `additional` 方法，它接受一个数据数组，将其中的数据添加到资源响应中：

```php
return User::all()
    ->load('roles')
    ->toResourceCollection()
    ->additional(['meta' => [
        'key' => 'value',
    ]]);
```

<a name="jsonapi-resources"></a>
## JSON:API 资源

Laravel 内置了 `JsonApiResource`，这一资源类能生成符合 [JSON:API 规范](https://jsonapi.org/)的响应。它继承自标准的 `JsonResource` 类，自动处理资源对象结构、关联、稀疏字段集、关联包含及属性的惰性求值，并将 `Content-Type` 响应头设置为 `application/vnd.api+json`。

> [!NOTE]
> Laravel 的 JSON:API 资源负责响应的序列化。如果你还需要解析传入的 JSON:API 查询参数，例如过滤和排序参数，[Spatie 的 Laravel Query Builder](https://spatie.be/docs/laravel-query-builder) 是很好的配套扩展包。

<a name="generating-jsonapi-resources"></a>
### 生成 JSON:API 资源

要生成 JSON:API 资源，可以使用 `make:resource` Artisan 命令并添加 `--json-api` 选项：

```shell
php artisan make:resource PostResource --json-api
```

生成的类会继承 `Illuminate\Http\Resources\JsonApi\JsonApiResource`，并包含供你定义的 `$attributes` 和 `$relationships` 属性：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\JsonApi\JsonApiResource;

class PostResource extends JsonApiResource
{
    /**
     * 资源的属性。
     */
    public $attributes = [
        // ...
    ];

    /**
     * 资源的关联。
     */
    public $relationships = [
        // ...
    ];
}
```

JSON:API 资源可以像标准资源一样，从路由和控制器返回：

```php
use App\Http\Resources\PostResource;
use App\Models\Post;

Route::get('/api/posts/{post}', function (Post $post) {
    return new PostResource($post);
});
```

或者，为方便起见，你可以使用模型的 `toResource` 方法：

```php
Route::get('/api/posts/{post}', function (Post $post) {
    return $post->toResource();
});
```

这会生成一个符合 JSON:API 规范的响应：

```json
{
    "data": {
        "id": "1",
        "type": "posts",
        "attributes": {
            "title": "Hello World",
            "body": "This is my first post."
        }
    }
}
```

要返回 JSON:API 资源集合，可以使用 `collection` 方法或便捷方法 `toResourceCollection`：

```php
return PostResource::collection(Post::all());

return Post::all()->toResourceCollection();
```

<a name="defining-jsonapi-attributes"></a>
### 定义属性

你可以通过两种方式，定义 JSON:API 资源中应包含的属性。

最简单的方式是在资源上定义 `$attributes` 属性。你可以将属性名称列为数组的值，这些属性会直接从底层模型读取：

```php
public $attributes = [
    'title',
    'body',
    'created_at',
];
```

如果某个属性的计算开销较大，你可以在 `toAttributes` 返回的数组中以闭包形式提供该属性，这样只有在响应确实需要它时才会求值。

或者，如果希望完全控制资源属性，你可以重写资源上的 `toAttributes` 方法：

```php
/**
 * 获取资源的属性。
 *
 * @return array<string, mixed>
 */
public function toAttributes(Request $request): array
{
    return [
        'title' => $this->title,
        'body' => $this->body,
        'is_published' => fn () => $this->published_at !== null,
        'created_at' => $this->created_at,
        'updated_at' => $this->updated_at,
    ];
}
```

<a name="defining-jsonapi-relationships"></a>
### 定义关联

JSON:API 资源支持定义符合 JSON:API 规范的关联。只有客户端通过 `include` 查询参数请求关联时，才会序列化这些关联。

#### `$relationships` 属性

你可以通过资源上的 `$relationships` 属性，定义允许包含的关联：

```php
public $relationships = [
    'author',
    'comments',
];
```

将关联名称列为数组的值时，Laravel 会解析对应的 Eloquent 关联，并自动查找相应的资源类。如果需要显式指定资源类，可以使用键与类的对应关系来定义该关联：

```php
use App\Http\Resources\UserResource;

public $relationships = [
    'author' => UserResource::class,
    'comments',
];
```

你也可以重写资源上的 `toRelationships` 方法：

```php
/**
 * 获取资源的关联。
 */
public function toRelationships(Request $request): array
{
    return [
        'author' => UserResource::class,
        'comments' => fn () => CommentResource::collection(
            $request->user()->is($this->resource)
                ? $this->comments
                : $this->comments->where('is_public', true),
        ),
    ];
}
```

使用闭包能让你更灵活地控制关联数据，同时仍然只在客户端请求时才解析该关联。

#### 包含关联

客户端可以使用 `include` 查询参数请求关联资源：

```
GET /api/posts/1?include=author,comments
```

生成的响应会在 `relationships` 键中包含资源标识符对象，并在顶层 `included` 数组中包含完整的资源对象：

```json
{
    "data": {
        "id": "1",
        "type": "posts",
        "attributes": {
            "title": "Hello World"
        },
        "relationships": {
            "author": {
                "data": {
                    "id": "1",
                    "type": "users"
                }
            },
            "comments": {
                "data": [
                    {
                        "id": "1",
                        "type": "comments"
                    }
                ]
            }
        }
    },
    "included": [
        {
            "id": "1",
            "type": "users",
            "attributes": {
                "name": "Taylor Otwell"
            }
        },
        {
            "id": "1",
            "type": "comments",
            "attributes": {
                "body": "Great post!"
            }
        }
    ]
}
```

可以使用点表示法包含嵌套关联：

```
GET /api/posts/1?include=comments.author
```

<a name="jsonapi-relationship-depth"></a>
#### 关联深度

默认情况下，包含嵌套关联时会受到最大深度的限制。你可以使用 `maxRelationshipDepth` 方法自定义这一限制，通常在应用的某个服务提供者中调用：

```php
use Illuminate\Http\Resources\JsonApi\JsonApiResource;

JsonApiResource::maxRelationshipDepth(3);
```

<a name="jsonapi-resource-type-and-id"></a>
### 资源类型与 ID

默认情况下，资源的 `type` 由资源类名推导而来。例如，`PostResource` 生成的类型为 `posts`，`BlogPostResource` 生成的类型为 `blog_posts`。资源的 `id` 则从模型的主键解析而来。

如果需要自定义这些值，你可以重写资源上的 `toType` 和 `toId` 方法：

```php
/**
 * 获取资源的类型。
 */
public function toType(Request $request): string
{
    return 'articles';
}

/**
 * 获取资源的 ID。
 */
public function toId(Request $request): string
{
    return (string) $this->uuid;
}
```

当资源类型需要与其类名不同时，这尤其有用。例如，`AuthorResource` 包裹的是 `User` 模型，但应输出 `authors` 类型。

<a name="jsonapi-sparse-fieldsets-and-includes"></a>
### 稀疏字段集与关联包含

JSON:API 资源支持[稀疏字段集](https://jsonapi.org/format/#fetching-sparse-fieldsets)，允许客户端使用 `fields` 查询参数，为每种资源类型只请求特定的属性：

```
GET /api/posts?fields[posts]=title,created_at&fields[users]=name
```

这样，`posts` 资源中只会包含 `title` 和 `created_at` 属性，`users` 资源中只会包含 `name` 属性。

<a name="jsonapi-ignoring-query-string"></a>
#### 忽略查询字符串

如果希望为某个资源响应禁用稀疏字段集过滤，你可以调用 `ignoreFieldsAndIncludesInQueryString` 方法：

```php
return $post->toResource()
    ->ignoreFieldsAndIncludesInQueryString();
```

<a name="jsonapi-including-previously-loaded-relationships"></a>
#### 包含之前已加载的关联

默认情况下，只有通过 `include` 查询参数请求关联时，响应中才会包含该关联。如果希望忽略查询字符串，包含所有之前已预加载的关联，你可以调用 `includePreviouslyLoadedRelationships` 方法：

```php
return $post->load('author', 'comments')
    ->toResource()
    ->includePreviouslyLoadedRelationships();
```

<a name="jsonapi-links-and-meta"></a>
### 链接与元数据

你可以通过重写资源上的 `toLinks` 和 `toMeta` 方法，为 JSON:API 资源对象添加链接与元信息：

```php
/**
 * 获取资源的链接。
 */
public function toLinks(Request $request): array
{
    return [
        'self' => route('api.posts.show', $this->resource),
    ];
}

/**
 * 获取资源的元信息。
 */
public function toMeta(Request $request): array
{
    return [
        'readable_created_at' => $this->created_at->diffForHumans(),
    ];
}
```

这会在响应的资源对象中添加 `links` 和 `meta` 键：

```json
{
    "data": {
        "id": "1",
        "type": "posts",
        "attributes": {
            "title": "Hello World"
        },
        "links": {
            "self": "https://example.com/api/posts/1"
        },
        "meta": {
            "readable_created_at": "2 hours ago"
        }
    }
}
```

<a name="resource-responses"></a>
## 资源响应

如前所述，资源可以直接从路由和控制器返回：

```php
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return User::findOrFail($id)->toResource();
});
```

不过，有时你可能需要在响应发送给客户端之前，自定义传出的 HTTP 响应。有两种方式可以做到这一点。首先，你可以在资源上链式调用 `response` 方法。该方法会返回 `Illuminate\Http\JsonResponse` 实例，让你能够完全控制响应头：

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/user', function () {
    return User::find(1)
        ->toResource()
        ->response()
        ->header('X-Value', 'True');
});
```

你也可以直接在资源上定义 `withResponse` 方法。当资源作为响应中的最外层资源返回时，就会调用该方法：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    /**
     * 将资源转换为数组。
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
        ];
    }

    /**
     * 自定义传出的资源响应。
     */
    public function withResponse(Request $request, JsonResponse $response): void
    {
        $response->header('X-Value', 'True');
    }
}
```
