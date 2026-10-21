
# Eloquent: API 资源

- [介绍](#introduction)
- [生成资源](#generating-resources)
- [概念概述](#concept-overview)
    - [资源集合](#resource-collections)
- [编写资源](#writing-resources)
    - [数据包装](#data-wrapping)
    - [分页](#pagination)
    - [条件属性](#conditional-attributes)
    - [条件关系](#conditional-relationships)
    - [添加元数据](#adding-meta-data)
- [资源响应](#resource-responses)

<a name="introduction"></a>
## 介绍

在构建API时，你可能需要一个 Eloquent 模型和 JSON 响应之间的转换层。例如，您可能希望仅为部分用户显示某些属性；或者您可能希望在模型的 JSON 响应中始终包含某些关系。 Eloquent 资源类使您能够以简洁明了的方式轻松地将模型及模型集合转换为 JSON 格式。

当然，你可以总是使用 Eloquent 模型/集合的`toJson`方法来将他们转换为JSON；但是 Eloquent 资源为您提供了更精细且更强大的控制能力，以实现对您的模型及其关系的 JSON 序列化管理。

<a name="generating-resources"></a>
## 生成资源

你可以使用 Artisan 命令 `make:resource` 来生成资源。默认情况下，资源会存放在您的应用程序的 `app/Http/Resources` 目录中。资源类继承自 `Illuminate\Http\Resources\Json\JsonResource` 类：

```shell
php artisan make:resource UserResource
```

<a name="generating-resource-collections"></a>
#### 资源集合

除了生成能够改变单个模型的资源外，您还可以生成能够对模型集合进行转换的资源。这使得您的 JSON 响应能够包含与特定资源的整个集合相关的链接和其他元信息。



要创建资源集合 ( Resource Collection )，您应该在创建资源时使用 `--collection` 参数。或者，在资源名称中包含`Collection`一词也会指示 Laravel 创建资源集合。资源集合继承自 `Illuminate\Http\Resources\Json\ResourceCollection` 类:

```shell
php artisan make:resource User --collection

php artisan make:resource UserCollection
```

<a name="concept-overview"></a>
## 概念概述

> [!NOTE]
> 这是对资源和资源集合 ( Resource Collection ) 的高级概述。我们强烈建议您阅读本文档的其他部分，以更深入地了解资源提供的自定义功能和强大功能。

在深入探讨编写 Resource 时可用的所有选项之前，让我们先从宏观角度了解一下 Resource 在 Laravel 中的使用方式, Resource 类代表一个需要转换为 JSON 结构的单个模型, 例如，这是一个简单的 `UserResource` 资源类:

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    /**
     * 将资源转换为数组
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

每个资源类都定义了一个 `toArray` 方法，该方法返回一个属性数组，当资源作为路由或控制器方法的响应返回时，这些属性将被转换为 JSON 格式。

请注意，我们可以直接通过 `$this` 变量访问模型的属性, 这是因为资源类会自动将属性和方法的访问代理到底层模型，以便于访问。资源定义完成后，可以从路由或控制器返回该资源。资源通过其构造函数接收底层模型实例。:

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return new UserResource(User::findOrFail($id));
});
```



为方便起见，你可以使用模型的 `toResource` 方法，该方法将遵循框架惯例，自动找到模型对应的资源：

```php
return User::findOrFail($id)->toResource();
```

调用 `toResource` 方法时，Laravel 会尝试在最接近模型命名空间的 `Http\Resources` 命名空间内，寻找与模型名称匹配且可选地以 `Resource` 为后缀的资源 。

<a name="resource-collections"></a>
### 资源集合

如果你要返回资源集合或分页响应，在路由或控制器中创建资源实例时，应该使用资源类提供的 `collection` 方法：

```php
use App\Http\Resources\UserResource;
use App\Models\User;

Route::get('/users', function () {
    return UserResource::collection(User::all());
});
```

或者，为了方便操作，你可以使用 Eloquent 集合的 `toResourceCollection` 方法，该方法将遵循框架惯例，自动找到模型对应的资源集合：

```php
return User::all()->toResourceCollection();
```

调用 `toResourceCollection` 方法时，Laravel 会尝试在最接近模型命名空间的 `Http\Resources` 命名空间内，寻找与模型名称匹配且以 `Collection` 为后缀的资源集合 。

<a name="custom-resource-collections"></a>
#### 自定义资源集合

默认情况下，资源集合不允许添加任何可能需要与集合一同返回的自定义元数据。如果你想自定义资源集合响应，可以创建一个专用资源来表示该集合：

```shell
php artisan make:resource UserCollection
```

生成资源集合类后，你可以轻松定义任何应包含在响应中的元数据：

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

定义好资源集合后，可以从路由或控制器返回它：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::all());
});
```

或者，为方便起见，你可以使用 Eloquent 集合的 `toResourceCollection` 方法，该方法会依据框架约定，自动找到模型对应的底层资源集合：

```php
return User::all()->toResourceCollection();
```

调用 `toResourceCollection` 方法时，Laravel 会尝试在最接近模型命名空间的 `Http\Resources` 命名空间内，定位与模型名称匹配且以 `Collection` 为后缀的资源集合。

<a name="preserving-collection-keys"></a>
#### 保留集合键

从路由返回资源集合时，Laravel 会重置集合的键，使其按数字顺序排列。不过，你可以在资源类中添加一个 `preserveKeys` 属性，表明是否应保留集合的原始键：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    /**
     * 表明资源集合的键是否应保留。
     *
     * @var bool
     */
    public $preserveKeys = true;
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

通常，资源集合的 `$this->collection` 属性会自动填充为将集合中的每个项目映射到其单个资源类的结果。单个资源类被假定为集合类名去掉类名末尾的 `Collection` 部分。此外，根据个人偏好，单个资源类可能带有也可能不带有 `Resource` 后缀。

例如，`UserCollection` 会尝试将给定的用户实例映射到 `UserResource` 资源。要自定义此行为，可以重写资源集合的 `$collects` 属性：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    /**
     * 此资源所收集的资源。
     *
     * @var string
     */
    public $collects = Member::class;
}
```

<a name="writing-resources"></a>
## 编写资源

> [!NOTE]
> 如果您尚未阅读 [概述](#concept-overview)，强烈建议在继续阅读本文档之前先阅读该部分。

资源只需将给定的模型转换为数组。因此，每个资源都包含一个 `toArray` 方法，该方法将模型的属性转换为适合 API 的数组，以便从应用程序的路由或控制器返回：

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

定义好资源后，可以直接从路由或控制器返回：

```php
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return User::findOrFail($id)->toUserResource();
});
```

<a name="relationships"></a>
#### 关联关系

如果希望在响应中包含相关资源，可以将它们添加到资源的 `toArray` 方法返回的数组中。在此示例中，我们将使用 `PostResource` 资源的 `collection` 方法，将用户的博客文章添加到资源响应中：

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
> 如果只想在关联关系已加载的情况下包含它们，请查看 [条件关联关系](#conditional-relationships) 的文档。

#### 资源集合（Resource Collections）

当资源（resource）将**单个模型**转换为数组时，**资源集合**则负责将**模型集合**转换为数组。
不过，并**不是绝对必须**为每一个模型都定义一个资源集合类，因为所有 Eloquent 模型集合都提供了 `toResourceCollection` 方法，可以**即时生成一个“临时（ad-hoc）”资源集合**：

```php
use App\Models\User;

Route::get('/users', function () {
    return User::all()->toResourceCollection();
});
```

然而，如果你需要**自定义随集合一起返回的元数据（meta data）**，则**有必要定义你自己的资源集合类**：

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

与单个资源类似，资源集合可以**直接从路由或控制器中返回**：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::all());
});
```

或者，为了方便起见，你也可以使用 Eloquent 集合的 `toResourceCollection` 方法，
该方法会**按照框架约定自动查找模型对应的底层资源集合类**：

```php
return User::all()->toResourceCollection();
```

在调用 `toResourceCollection` 方法时，Laravel 会尝试在**最接近模型命名空间的 `Http\Resources` 命名空间**中，
查找一个**名称与模型名匹配并以 `Collection` 结尾的资源集合类**。

### 数据包裹（Data Wrapping）

默认情况下，当资源响应被转换为 JSON 时，**最外层资源会被包裹在 `data` 键中**。
例如，一个典型的资源集合响应如下所示：

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



如果你希望**禁用最外层资源的包裹（wrapping）**，可以在基础类
`Illuminate\Http\Resources\Json\JsonResource` 上调用 `withoutWrapping` 方法。
通常，你应该在应用的 `AppServiceProvider` 或其他**在每个请求中都会加载的服务提供者**中调用该方法：

```php
<?php

namespace App\Providers;

use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册任何应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 引导任何应用服务。
     */
    public function boot(): void
    {
        JsonResource::withoutWrapping();
    }
}
```

> [!警告]
> `withoutWrapping` 方法**只会影响最外层的响应**，并不会移除你在自定义资源集合中**手动添加的 `data` 键**。

#### 包裹嵌套资源（Wrapping Nested Resources）

你可以**完全自由地决定资源关联关系的包裹方式**。
如果你希望**所有资源集合无论嵌套层级如何，都统一包裹在 `data` 键中**，
则应该为每个资源定义一个资源集合类，并在返回时将集合放入 `data` 键中。

你可能会担心这样会不会导致**最外层资源被包裹两次 `data` 键**。
不必担心，Laravel **永远不会让资源被意外地重复包裹**，
因此你无需关注正在转换的资源集合所处的嵌套层级：

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



### 数据包裹与分页

当通过资源响应返回**分页集合**时，即使已经调用了 `withoutWrapping` 方法，
Laravel 仍然会将资源数据**包裹在 `data` 键中**。
这是因为分页响应**始终包含 `meta` 和 `links` 键**，用于提供分页器当前状态的信息：

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

### 分页

你可以将 **Laravel 分页器实例** 传递给资源的 `collection` 方法，
或传递给一个自定义的资源集合类：

```php
use App\Http\Resources\UserCollection;
use App\Models\User;

Route::get('/users', function () {
    return new UserCollection(User::paginate());
});
```

或者，为了方便起见，你也可以使用分页器的 `toResourceCollection` 方法，
该方法会**按照框架约定自动查找分页模型对应的底层资源集合类**：

```php
return User::paginate()->toResourceCollection();
```

分页响应**始终包含 `meta` 和 `links` 键**，用于描述分页器的状态信息：

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

#### 自定义分页信息（Customizing the Pagination Information）

如果你希望**自定义分页响应中 `links` 或 `meta` 键所包含的信息**，
可以在资源中定义一个 `paginationInformation` 方法。
该方法会接收 `$paginated` 数据以及 `$default` 信息数组，
其中 `$default` 是一个包含 `links` 和 `meta` 键的数组：

```php
/**
 * 为资源自定义分页信息。
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

有时，您可能希望仅在满足特定条件时才将某个属性包含在资源响应中。例如，您可能希望仅在当前用户是 “Admin” 时才包含某个值。Laravel 提供了多种辅助方法来帮助您处理这种情况。您可以使用 `when` 方法有条件地将属性添加到资源响应中。:

```php
/**
 * 将资源转换为数组
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

在此示例中，只有当已认证用户的 `isAdmin` 方法返回 `true` 时，`secret` 键才会在最终的资源响应中返回。如果该方法返回 `false`，则在将资源响应发送给客户端之前，`secret` 键将被从响应中移除。`when` 方法允许您以更简洁的方式定义资源，而无需在构建数组时使用条件语句。

`when` 方法也接受一个闭包作为第二个参数，这样您就可以仅在给定条件为 `true` 时才计算结果值:

```php
'secret' => $this->when($request->user()->isAdmin(), function () {
    return 'secret-value';
}),
```

`whenHas` 方法可用于在底层模型中实际存在某个属性时才包含该属性:

```php
'name' => $this->whenHas('name'),
```

此外，`whenNotNull` 方法可用于在属性不为 null 时在资源响应中包含属性:

```php
'name' => $this->whenNotNull($this->name),
```



## 合并条件属性

有时候，你可能有**多个属性**，它们都只应该在**同一个条件成立时**才被包含在资源响应中。
在这种情况下，你可以使用 `mergeWhen` 方法，**只有当给定条件为 `true` 时**，才将这些属性包含进响应里：

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

同样地，如果给定的条件为 `false`，这些属性会在发送给客户端之前**从资源响应中被移除**。

> [!警告]
> `mergeWhen` 方法不应该用在**同时混合字符串键和数字键的数组中**。 此外，它也不应该用在**数字键不是按顺序排列的数组中**。

## 条件关系（Conditional Relationships）

除了有条件地加载属性之外，你还可以根据**模型上的关系是否已经被加载**，来有条件地在资源响应中包含这些关系。
这样可以让你的**控制器**决定要在模型上加载哪些关系，而你的**资源类**只在这些关系确实已经被加载时才将它们包含进响应中。
最终，这会让你更容易在资源中避免出现 **“N+1 查询”** 问题。
可以使用 `whenLoaded` 方法来有条件地加载一个关系。
为了避免不必要地加载关系，这个方法接收的是**关系名称**，而不是关系本身：

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



在这个示例中，如果该关系**尚未被加载**，`posts` 键会在资源响应发送给客户端之前**被移除**。

## 条件关系数量

除了有条件地包含关系之外，你还可以根据**关系的数量是否已经在模型上加载**，来有条件地在资源响应中包含关系的“数量”：

```php
new UserResource($user->loadCount('posts'));
```

`whenCounted` 方法可用于在资源响应中**有条件地包含某个关系的数量**。
如果该关系的数量不存在，这个方法可以避免不必要地包含该属性：

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

在这个示例中，如果 `posts` 关系的数量**没有被加载**，`posts_count` 键会在资源响应发送给客户端之前**被移除**。


其他类型的聚合结果，例如 `avg`、`sum`、`min` 和 `max`，也可以通过 `whenAggregated` 方法进行条件加载：

```php
'words_avg' => $this->whenAggregated('posts', 'words', 'avg'),
'words_sum' => $this->whenAggregated('posts', 'words', 'sum'),
'words_min' => $this->whenAggregated('posts', 'words', 'min'),
'words_max' => $this->whenAggregated('posts', 'words', 'max'),
```

## 条件中间表信息（Conditional Pivot Information）

除了在资源响应中有条件地包含关系信息之外，你还可以使用 `whenPivotLoaded` 方法，**有条件地包含多对多关系中间表的数据**。

`whenPivotLoaded` 方法的第一个参数是**中间表的名称**。
第二个参数应该是一个闭包，用于在模型上存在中间表信息时，返回需要返回的值：

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



如果你的关系使用了 [自定义中间表模型](/docs/laravel/12.x/eloquent-relationships#defining-custom-intermediate-table-models)，你可以将中间表模型的实例作为第一个参数传递给 `whenPivotLoaded` 方法：

```php
'expires_at' => $this->whenPivotLoaded(new Membership, function () {
    return $this->pivot->expires_at;
}),
```

如果你的中间表使用了除了 `pivot` 之外的访问器，你可以使用 `whenPivotLoadedAs` 方法：

```php
/**
 * 将资源转换为数组
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

### 添加元数据

一些 JSON API 标准要求在资源和资源集合响应中添加元数据。这通常包括指向资源或相关资源的 `links`，或关于资源本身的元数据。如果你需要返回资源的附加元数据，可以在 `toArray` 方法中包含它。例如，在转换资源集合时，你可能会包含 `links` 信息：

```php
/**
 * 将资源转换为数组
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

在从资源返回附加元数据时，你不必担心意外覆盖 Laravel 在返回分页响应时自动添加的 `links` 或 `meta` 键。你定义的任何附加 `links` 都会与分页器提供的链接合并。

#### 顶层元数据

有时，你可能希望仅在资源是最外层资源时才包含某些元数据。通常，这包括关于整个响应的元信息。要定义这些元数据，请向你的资源类添加一个 `with` 方法。该方法应返回一个数组，只有当资源是最外层资源被转换时才会包含这些元数据：

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    /**
     * 将资源集合转换为数组
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return parent::toArray($request);
    }

    /**
     * 获取应随资源数组返回的附加数据
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
#### 在构建资源时添加元数据

你还可以在路由或控制器中构造资源实例时添加顶级数据。`additional` 方法，在所有资源上都可用，接受一个应添加到资源响应的数据数组：

```php
return User::all()
    ->load('roles')
    ->toResourceCollection()
    ->additional(['meta' => [
        'key' => 'value',
    ]]);
```

<a name="resource-responses"></a>
## 资源响应

如你所读，资源可以直接从路由和控制器返回：

```php
use App\Models\User;

Route::get('/user/{id}', function (string $id) {
    return User::findOrFail($id)->toResource();
});
```

然而，有时你可能需要在发送给客户端之前自定义出站 HTTP 响应。有两种方法可以实现这一点。首先，你可以在资源上链式调用 `response` 方法。此方法将返回一个 `Illuminate\Http\JsonResponse` 实例，让你完全控制响应的头：

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

或者，你可以在资源本身中定义一个 `withResponse` 方法。当资源作为响应中的最外层资源返回时，将调用此方法：

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
     * 自定义资源的出站响应。
     */
    public function withResponse(Request $request, JsonResponse $response): void
    {
        $response->header('X-Value', 'True');
    }
}
```
