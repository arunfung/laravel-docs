# 验证

- [简介](#introduction)
- [验证快速入门](#validation-quickstart)
    - [定义路由](#quick-defining-the-routes)
    - [创建控制器](#quick-creating-the-controller)
    - [编写验证逻辑](#quick-writing-the-validation-logic)
    - [显示验证错误](#quick-displaying-the-validation-errors)
    - [重新填充表单](#repopulating-forms)
    - [关于可选字段的说明](#a-note-on-optional-fields)
    - [验证错误响应格式](#validation-error-response-format)
- [表单请求验证](#form-request-validation)
    - [创建表单请求](#creating-form-requests)
    - [授权表单请求](#authorizing-form-requests)
    - [自定义错误消息](#customizing-the-error-messages)
    - [为验证准备输入数据](#preparing-input-for-validation)
- [手动创建验证器](#manually-creating-validators)
    - [自动重定向](#automatic-redirection)
    - [命名错误包](#named-error-bags)
    - [自定义错误消息](#manual-customizing-the-error-messages)
    - [执行额外验证](#performing-additional-validation)
- [使用已验证的输入](#working-with-validated-input)
- [处理错误消息](#working-with-error-messages)
    - [在语言文件中指定自定义消息](#specifying-custom-messages-in-language-files)
    - [在语言文件中指定属性](#specifying-attribute-in-language-files)
    - [在语言文件中指定值](#specifying-values-in-language-files)
- [可用的验证规则](#available-validation-rules)
    - [规则构建器](#rule-builders)
- [有条件地添加规则](#conditionally-adding-rules)
- [验证数组](#validating-arrays)
    - [验证嵌套数组输入](#validating-nested-array-input)
    - [错误消息索引和位置](#error-message-indexes-and-positions)
- [验证文件](#validating-files)
- [验证密码](#validating-passwords)
- [从 JSON Schema 派生规则](#deriving-rules-from-json-schemas)
- [自定义验证规则](#custom-validation-rules)
    - [使用规则对象](#using-rule-objects)
    - [使用闭包](#using-closures)
    - [隐式规则](#implicit-rules)

<a name="introduction"></a>
## 简介

Laravel 提供了多种不同的方式来验证应用程序接收到的数据。最常见的方式是使用所有传入 HTTP 请求都可以使用的 `validate` 方法。不过，我们也会讨论其他验证方式。

Laravel 包含了各种方便的验证规则，你可以将这些规则应用于数据，甚至可以验证某个值在指定数据库表中是否唯一。我们将详细介绍这些验证规则中的每一项，以便你熟悉 Laravel 的所有验证功能。

<a name="validation-quickstart"></a>
## 验证快速入门

为了了解 Laravel 强大的验证功能，让我们来看一个完整的示例，其中包括验证表单以及向用户显示错误消息。通过阅读这个高层次的概述，你将能够对如何使用 Laravel 验证传入的请求数据有一个良好的总体理解：

<a name="quick-defining-the-routes"></a>
### 定义路由

首先，假设我们在 `routes/web.php` 文件中定义了以下路由：

```php
use App\Http\Controllers\PostController;

Route::get('/post/create', [PostController::class, 'create']);
Route::post('/post', [PostController::class, 'store']);
```

`GET` 路由将显示一个供用户创建新博客文章的表单，而 `POST` 路由会将新的博客文章存储到数据库中。

<a name="quick-creating-the-controller"></a>
### 创建控制器

接下来，让我们看一个用于处理这些路由传入请求的简单控制器。我们暂时将 `store` 方法留空：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class PostController extends Controller
{
    /**
     * 显示用于创建新博客文章的表单。
     */
    public function create(): View
    {
        return view('post.create');
    }

    /**
     * 存储新的博客文章。
     */
    public function store(Request $request): RedirectResponse
    {
        // 验证并存储博客文章...

        $post = /** ... */

        return to_route('post.show', ['post' => $post->id]);
    }
}
```

<a name="quick-writing-the-validation-logic"></a>
### 编写验证逻辑

现在，我们可以在 `store` 方法中填入用于验证新博客文章的逻辑。为此，我们将使用 `Illuminate\Http\Request` 对象提供的 `validate` 方法。如果验证规则通过，你的代码将继续正常执行；但是，如果验证失败，将抛出一个 `Illuminate\Validation\ValidationException` 异常，并且会自动向用户返回适当的错误响应。

如果在传统 HTTP 请求期间验证失败，将会生成一个重定向到上一个 URL 的响应。如果传入请求是 XHR 请求，则会返回一个[包含验证错误消息的 JSON 响应](#validation-error-response-format)。

为了更好地理解 `validate` 方法，让我们回到 `store` 方法：

```php
/**
 * 存储新的博客文章。
 */
public function store(Request $request): RedirectResponse
{
    $validated = $request->validate([
        'title' => ['required', 'unique:posts', 'max:255'],
        'body' => ['required'],
    ]);

    // 博客文章有效...

    return redirect('/posts');
}
```

如你所见，验证规则被传递给 `validate` 方法。不用担心——所有可用的验证规则都有[文档说明](#available-validation-rules)。再次说明，如果验证失败，会自动生成适当的响应。如果验证通过，我们的控制器将继续正常执行。

此外，你还可以使用 `validateWithBag` 方法验证请求，并将所有错误消息存储在一个[命名错误包](#named-error-bags)中：

```php
$validated = $request->validateWithBag('post', [
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
]);
```

<a name="stopping-on-first-validation-failure"></a>
#### 在第一次验证失败时停止

有时，你可能希望某个属性在第一次验证失败后就停止继续执行验证规则。为此，可以为该属性指定 `bail` 规则：

```php
$request->validate([
    'title' => ['bail', 'required', 'unique:posts', 'max:255'],
    'body' => ['required'],
]);
```

在这个示例中，如果 `title` 属性上的 `unique` 规则验证失败，则不会再检查 `max` 规则。规则将按照它们被指定的顺序进行验证。

<a name="a-note-on-nested-attributes"></a>
#### 关于嵌套属性的说明

如果传入的 HTTP 请求包含“嵌套”字段数据，你可以在验证规则中使用“点”语法来指定这些字段：

```php
$request->validate([
    'title' => ['required', 'unique:posts', 'max:255'],
    'author.name' => ['required'],
    'author.description' => ['required'],
]);
```

另一方面，如果你的字段名称中包含一个字面意义上的句点，你可以通过使用反斜杠转义该句点，明确防止它被解释为“点”语法：

```php
$request->validate([
    'title' => ['required', 'unique:posts', 'max:255'],
    'v1\.0' => ['required'],
]);
```

<a name="quick-displaying-the-validation-errors"></a>
### 显示验证错误

那么，如果传入请求中的字段没有通过给定的验证规则会怎样？如前所述，Laravel 会自动将用户重定向回他们之前的位置。此外，所有验证错误和[请求输入](/docs/{{version}}/requests#retrieving-old-input)都会自动被[闪存到 session 中](/docs/{{version}}/session#flash-data)。

`Illuminate\View\Middleware\ShareErrorsFromSession` 中间件会将一个 `$errors` 变量共享给应用程序的所有视图，该中间件由 `web` 中间件组提供。当应用了该中间件后，视图中将始终可以使用 `$errors` 变量，因此你可以方便地假定 `$errors` 变量始终已定义，并且可以安全使用。`$errors` 变量将是一个 `Illuminate\Support\MessageBag` 实例。有关如何使用此对象的更多信息，[请查看其文档](#working-with-error-messages)。

因此，在我们的示例中，当验证失败时，用户将被重定向到控制器的 `create` 方法，从而允许我们在视图中显示错误消息：

```blade
<!-- /resources/views/post/create.blade.php -->

<h1>Create Post</h1>

@if ($errors->any())
    <div class="alert alert-danger">
        <ul>
            @foreach ($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

<!-- 创建文章表单 -->
```

<a name="quick-customizing-the-error-messages"></a>
#### 自定义错误消息

Laravel 的每个内置验证规则都有一条错误消息，这些消息位于应用程序的 `lang/en/validation.php` 文件中。如果你的应用程序没有 `lang` 目录，可以使用 `lang:publish` Artisan 命令让 Laravel 创建它。

在 `lang/en/validation.php` 文件中，你会找到每条验证规则对应的翻译条目。你可以根据应用程序的需要自由更改或修改这些消息。

此外，你还可以将此文件复制到其他语言目录中，以便将这些消息翻译成应用程序所使用的语言。要了解更多关于 Laravel 本地化的信息，请查看完整的[本地化文档](/docs/{{version}}/localization)。

> [!NOTE]
> 默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果你想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

<a name="quick-xhr-requests-and-validation"></a>
#### XHR 请求和验证

在这个示例中，我们使用传统表单向应用程序发送数据。然而，许多应用程序会从由 JavaScript 驱动的前端接收 XHR 请求。在 XHR 请求期间使用 `validate` 方法时，Laravel 不会生成重定向响应。相反，Laravel 会生成一个[包含所有验证错误的 JSON 响应](#validation-error-response-format)。这个 JSON 响应会以 422 HTTP 状态码发送。

<a name="the-at-error-directive"></a>
#### `@error` 指令

你可以使用 `@error` [Blade](/docs/{{version}}/blade) 指令快速判断某个给定属性是否存在验证错误消息。在 `@error` 指令中，你可以输出 `$message` 变量来显示错误消息：

```blade
<!-- /resources/views/post/create.blade.php -->

<label for="title">Post Title</label>

<input
    id="title"
    type="text"
    name="title"
    class="@error('title') is-invalid @enderror"
/>

@error('title')
    <div class="alert alert-danger">{{ $message }}</div>
@enderror
```

如果你正在使用[命名错误包](#named-error-bags)，可以将错误包的名称作为第二个参数传递给 `@error` 指令：

```blade
<input ... class="@error('title', 'post') is-invalid @enderror">
```

<a name="repopulating-forms"></a>
### 重新填充表单

当 Laravel 因验证错误生成重定向响应时，框架会自动[将请求中的所有输入闪存到 session 中](/docs/{{version}}/session#flash-data)。这样做是为了让你能够在下一次请求期间方便地访问这些输入，并重新填充用户之前尝试提交的表单。

要获取上一次请求中闪存的输入，可以在 `Illuminate\Http\Request` 实例上调用 `old` 方法。`old` 方法会从 [session](/docs/{{version}}/session) 中取出之前闪存的输入数据：

```php
$title = $request->old('title');
```

Laravel 还提供了一个全局的 `old` 辅助函数。如果你在 [Blade 模板](/docs/{{version}}/blade) 中显示旧输入，使用 `old` 辅助函数来重新填充表单会更加方便。如果给定字段不存在旧输入，则会返回 `null`：

```blade
<input type="text" name="title" value="{{ old('title') }}">
```

<a name="a-note-on-optional-fields"></a>
### 关于可选字段的说明

默认情况下，Laravel 会在应用程序的全局中间件栈中包含 `TrimStrings` 和 `ConvertEmptyStringsToNull` 中间件。因此，如果你不希望验证器将 `null` 值视为无效，通常需要将“可选”请求字段标记为 `nullable`。例如：

```php
$request->validate([
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
    'publish_at' => ['nullable', 'date'],
]);
```

在这个示例中，我们指定 `publish_at` 字段可以是 `null`，也可以是一个有效的日期表示。如果没有在规则定义中添加 `nullable` 修饰符，验证器会将 `null` 视为无效日期。

<a name="validation-error-response-format"></a>
### 验证错误响应格式

当你的应用程序抛出 `Illuminate\Validation\ValidationException` 异常，并且传入的 HTTP 请求期望接收 JSON 响应时，Laravel 会自动为你格式化错误消息，并返回一个 `422 Unprocessable Entity` HTTP 响应。

下面，你可以查看一个验证错误的 JSON 响应格式示例。请注意，嵌套的错误键会被扁平化为“点”表示法格式：

```json
{
    "message": "The team name field must be a string. (and 4 more errors)",
    "errors": {
        "team_name": [
            "The team name field must be a string.",
            "The team name field must be at least 1 characters."
        ],
        "authorization.role": [
            "The selected authorization.role is invalid."
        ],
        "users.0.email": [
            "The users.0.email field is required."
        ],
        "users.2.email": [
            "The users.2.email field must be a valid email address."
        ]
    }
}
```

<a name="form-request-validation"></a>
## 表单请求验证

<a name="creating-form-requests"></a>
### 创建表单请求

对于更复杂的验证场景，你可能希望创建一个“表单请求”。表单请求是自定义的请求类，它们封装了自身的验证和授权逻辑。要创建一个表单请求类，你可以使用 `make:request` Artisan CLI 命令：

```shell
php artisan make:request StorePostRequest
```

生成的表单请求类将放置在 `app/Http/Requests` 目录中。如果该目录不存在，当你运行 `make:request` 命令时会自动创建。Laravel 生成的每个表单请求都有两个方法：`authorize` 和 `rules`。

正如你可能已经猜到的，`authorize` 方法负责确定当前已通过身份验证的用户是否可以执行该请求所代表的操作，而 `rules` 方法则返回应该应用于请求数据的验证规则：

```php
/**
 * 获取应用于该请求的验证规则。
 *
 * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
 */
public function rules(): array
{
    return [
        'title' => ['required', 'unique:posts', 'max:255'],
        'body' => ['required'],
    ];
}
```

> [!NOTE]
> 你可以在 `rules` 方法的签名中对所需的任何依赖项进行类型提示。它们会通过 Laravel [服务容器](/docs/{{version}}/container)自动解析。

那么，验证规则是如何被执行的呢？你只需要在控制器方法中对该请求进行类型提示即可。传入的表单请求会在控制器方法被调用之前进行验证，这意味着你不需要在控制器中加入任何验证逻辑：

```php
/**
 * 存储新的博客文章。
 */
public function store(StorePostRequest $request): RedirectResponse
{
    // 传入的请求有效...

    // 获取已验证的输入数据...
    $validated = $request->validated();

    // 获取已验证输入数据的一部分...
    $validated = $request->safe()->only(['name', 'email']);
    $validated = $request->safe()->except(['name', 'email']);

    // 存储博客文章...

    return redirect('/posts');
}
```

如果验证失败，将生成一个重定向响应，把用户发送回之前的位置。错误信息也会被闪存到 session 中，以便进行显示。如果该请求是 XHR 请求，则会向用户返回一个状态码为 422 的 HTTP 响应，其中包含[验证错误的 JSON 表示](#validation-error-response-format)。

> [!NOTE]
> 需要为由 Inertia 驱动的 Laravel 前端添加实时表单请求验证吗？请查看 [Laravel Precognition](/docs/{{version}}/precognition)。

<a name="performing-additional-validation-on-form-requests"></a>
#### 执行额外验证

有时，你需要在初始验证完成后执行额外的验证。你可以使用表单请求的 `after` 方法来实现这一点。

`after` 方法应返回一个可调用对象或闭包组成的数组，这些内容会在验证完成后被调用。给定的可调用对象会接收一个 `Illuminate\Validation\Validator` 实例，使你可以在必要时添加额外的错误消息：

```php
use Illuminate\Validation\Validator;

/**
 * 获取请求的“after”验证可调用对象。
 */
public function after(): array
{
    return [
        function (Validator $validator) {
            if ($this->somethingElseIsInvalid()) {
                $validator->errors()->add(
                    'field',
                    'Something is wrong with this field!'
                );
            }
        }
    ];
}
```

如前所述，`after` 方法返回的数组也可以包含可调用类。这些类的 `__invoke` 方法将接收一个 `Illuminate\Validation\Validator` 实例：

```php
use App\Validation\ValidateShippingTime;
use App\Validation\ValidateUserStatus;
use Illuminate\Validation\Validator;

/**
 * 获取请求的“after”验证可调用对象。
 */
public function after(): array
{
    return [
        new ValidateUserStatus,
        new ValidateShippingTime,
        function (Validator $validator) {
            //
        }
    ];
}
```

<a name="request-stopping-on-first-validation-rule-failure"></a>
#### 在第一次验证失败时停止

通过向你的请求类添加 `StopOnFirstFailure` 属性，你可以通知验证器，一旦发生一次验证失败，就应该停止验证所有属性：

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\Attributes\StopOnFirstFailure;
use Illuminate\Foundation\Http\FormRequest;

#[StopOnFirstFailure]
class StorePostRequest extends FormRequest
{
    // ...
}
```

<a name="request-failing-on-unknown-fields"></a>
#### 遇到未知字段时失败

通过向你的请求类添加 `FailOnUnknownFields` 属性，你可以指示 Laravel 拒绝任何未在请求验证规则中定义的传入字段：

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\Attributes\FailOnUnknownFields;
use Illuminate\Foundation\Http\FormRequest;

#[FailOnUnknownFields]
class StorePostRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'title' => ['required', 'string'],
            'body' => ['required', 'string'],
        ];
    }
}
```

你也可以在 `AppServiceProvider` 中为所有表单请求全局启用此行为：

```php
use Illuminate\Foundation\Http\FormRequest;

/**
 * 启动任何应用程序服务。
 */
public function boot(): void
{
    FormRequest::failOnUnknownFields();
}
```

如果需要，你可以通过向该属性传递 `false`，为特定请求禁用此行为：

```php
#[FailOnUnknownFields(false)]
class PublicWebhookRequest extends FormRequest
{
    // ...
}
```

拒绝未知字段可以通过阻止意外的输入键进一步流入你的应用程序，为防止类似批量赋值的问题提供额外保护。不过，你仍然应该配置模型的 `$fillable` / `$guarded` 属性，并且只持久化可信的、经过验证的输入。

<a name="customizing-the-redirect-location"></a>
#### 自定义重定向位置

当表单请求验证失败时，会生成一个重定向响应，将用户发送回之前的位置。不过，你可以自由自定义此行为。为此，你可以在表单请求上使用 `RedirectTo` 属性：

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\Attributes\RedirectTo;
use Illuminate\Foundation\Http\FormRequest;

#[RedirectTo('/dashboard')]
class StorePostRequest extends FormRequest
{
    // ...
}
```

或者，如果你希望将用户重定向到一个命名路由，可以改用 `RedirectToRoute` 属性：

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\Attributes\RedirectToRoute;
use Illuminate\Foundation\Http\FormRequest;

#[RedirectToRoute('dashboard')]
class StorePostRequest extends FormRequest
{
    // ...
}
```

<a name="customizing-the-error-bag"></a>
#### 自定义错误包

当表单请求验证失败时，错误会被闪存到 `default` 错误包中。如果你需要将错误存储到另一个[命名错误包](#named-error-bags)中，可以在表单请求上使用 `ErrorBag` 属性：

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\Attributes\ErrorBag;
use Illuminate\Foundation\Http\FormRequest;

#[ErrorBag('login')]
class LoginRequest extends FormRequest
{
    // ...
}
```

<a name="authorizing-form-requests"></a>
### 授权表单请求

表单请求类还包含一个 `authorize` 方法。在这个方法中，你可以判断已认证用户是否确实有权限更新某个给定资源。例如，你可以判断用户是否确实拥有他们正在尝试更新的博客评论。通常，你会在这个方法中与[授权 Gate 和 Policy](/docs/{{version}}/authorization)进行交互：

```php
use App\Models\Comment;

/**
 * 判断用户是否有权限发起此请求。
 */
public function authorize(): bool
{
    $comment = Comment::find($this->route('comment'));

    return $comment && $this->user()->can('update', $comment);
}
```

由于所有表单请求都继承自 Laravel 的基础请求类，因此我们可以使用 `user` 方法访问当前已认证的用户。另外，请注意上面示例中对 `route` 方法的调用。这个方法允许你访问当前被调用路由中定义的 URI 参数，例如下面示例中的 `{comment}` 参数：

```php
Route::post('/comment/{comment}');
```

因此，如果你的应用程序使用了[路由模型绑定](/docs/{{version}}/routing#route-model-binding)，则可以通过将已解析的模型作为请求的属性来访问，从而让代码更加简洁：

```php
return $this->user()->can('update', $this->comment);
```

如果 `authorize` 方法返回 `false`，Laravel 会自动返回一个状态码为 403 的 HTTP 响应，并且你的控制器方法不会执行。

如果你打算在应用程序的其他部分处理该请求的授权逻辑，可以完全删除 `authorize` 方法，或者直接返回 `true`：

```php
/**
 * 判断用户是否有权限发起此请求。
 */
public function authorize(): bool
{
    return true;
}
```

> [!NOTE]
> 你可以在 `authorize` 方法的签名中对所需的任何依赖项进行类型提示。它们会通过 Laravel [服务容器](/docs/{{version}}/container)自动解析。

<a name="customizing-the-error-messages"></a>
### 自定义错误消息

你可以通过重写 `messages` 方法来自定义表单请求所使用的错误消息。该方法应返回一个由属性 / 规则对及其对应错误消息组成的数组：

```php
/**
 * 获取已定义验证规则的错误消息。
 *
 * @return array<string, string>
 */
public function messages(): array
{
    return [
        'title.required' => 'A title is required',
        'body.required' => 'A message is required',
    ];
}
```

<a name="customizing-the-validation-attributes"></a>
#### 自定义验证属性

Laravel 的许多内置验证规则错误消息中都包含一个 `:attribute` 占位符。如果你希望验证消息中的 `:attribute` 占位符被替换为自定义属性名称，可以通过重写 `attributes` 方法来指定自定义名称。该方法应返回一个由属性 / 名称对组成的数组：

```php
/**
 * 获取用于验证器错误的自定义属性。
 *
 * @return array<string, string>
 */
public function attributes(): array
{
    return [
        'email' => 'email address',
    ];
}
```

<a name="preparing-input-for-validation"></a>
### 为验证准备输入

如果你需要在应用验证规则之前，对请求中的任何数据进行准备或清理，可以使用 `prepareForValidation` 方法：

```php
use Illuminate\Support\Str;

/**
 * 为验证准备数据。
 */
protected function prepareForValidation(): void
{
    $this->merge([
        'slug' => Str::slug($this->slug),
    ]);
}
```

同样，如果你需要在验证完成后规范化任何请求数据，可以使用 `passedValidation` 方法：

```php
/**
 * 处理一次通过的验证尝试。
 */
protected function passedValidation(): void
{
    $this->replace(['name' => 'Taylor']);
}
```

<a name="manually-creating-validators"></a>
## 手动创建验证器

如果你不想使用请求上的 `validate` 方法，可以使用 `Validator` [门面](/docs/{{version}}/facades)手动创建一个验证器实例。门面上的 `make` 方法会生成一个新的验证器实例：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class PostController extends Controller
{
    /**
     * 存储新的博客文章。
     */
    public function store(Request $request): RedirectResponse
    {
        $validator = Validator::make($request->all(), [
            'title' => ['required', 'unique:posts', 'max:255'],
            'body' => ['required'],
        ]);

        if ($validator->fails()) {
            return redirect('/post/create')
                ->withErrors($validator)
                ->withInput();
        }

        // 获取已验证的输入...
        $validated = $validator->validated();

        // 获取已验证输入的一部分...
        $validated = $validator->safe()->only(['name', 'email']);
        $validated = $validator->safe()->except(['name', 'email']);

        // 存储博客文章...

        return redirect('/posts');
    }
}
```

传递给 `make` 方法的第一个参数是要进行验证的数据。第二个参数是一个验证规则数组，这些规则将应用于该数据。

在确定请求验证是否失败之后，你可以使用 `withErrors` 方法将错误消息闪存到 session 中。使用此方法时，重定向之后 `$errors` 变量会自动与你的视图共享，从而使你能够轻松地将错误消息显示给用户。`withErrors` 方法接受验证器、`MessageBag` 或 PHP `array`。

#### 在第一次验证失败时停止

`stopOnFirstFailure` 方法会通知验证器，一旦发生一次验证失败，就停止验证所有属性：

```php
if ($validator->stopOnFirstFailure()->fails()) {
    // ...
}
```

<a name="automatic-redirection"></a>
### 自动重定向

如果你想手动创建验证器实例，同时仍然利用 HTTP 请求的 `validate` 方法所提供的自动重定向功能，可以在现有的验证器实例上调用 `validate` 方法。如果验证失败，用户将被自动重定向；如果是 XHR 请求，则会[返回 JSON 响应](#validation-error-response-format)：

```php
Validator::make($request->all(), [
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
])->validate();
```

如果验证失败，你可以使用 `validateWithBag` 方法将错误消息存储到一个[命名错误包](#named-error-bags)中：

```php
Validator::make($request->all(), [
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
])->validateWithBag('post');
```

<a name="named-error-bags"></a>
### 命名错误包

如果一个页面上有多个表单，你可能希望为包含验证错误的 `MessageBag` 命名，这样就可以获取特定表单的错误消息。要实现这一点，可以将名称作为第二个参数传递给 `withErrors`：

```php
return redirect('/register')->withErrors($validator, 'login');
```

然后，你可以通过 `$errors` 变量访问已命名的 `MessageBag` 实例：

```blade
{{ $errors->login->first('email') }}
```

<a name="manual-customizing-the-error-messages"></a>
### 自定义错误消息

如果需要，你可以提供自定义错误消息，让验证器实例使用这些消息，而不是 Laravel 提供的默认错误消息。指定自定义消息有多种方式。首先，你可以将自定义消息作为第三个参数传递给 `Validator::make` 方法：

```php
$validator = Validator::make($input, $rules, $messages = [
    'required' => 'The :attribute field is required.',
]);
```

在这个示例中，`:attribute` 占位符会被替换为正在验证的字段的实际名称。你也可以在验证消息中使用其他占位符。例如：

```php
$messages = [
    'same' => 'The :attribute and :other must match.',
    'size' => 'The :attribute must be exactly :size.',
    'between' => 'The :attribute value :input is not between :min - :max.',
    'in' => 'The :attribute must be one of the following types: :values',
];
```

<a name="specifying-a-custom-message-for-a-given-attribute"></a>
#### 为给定属性指定自定义消息

有时，你可能只希望为某个特定属性指定自定义错误消息。你可以使用“点”表示法来实现。先指定属性名称，然后再指定规则：

```php
$messages = [
    'email.required' => 'We need to know your email address!',
];
```

<a name="specifying-custom-attribute-values"></a>
#### 指定自定义属性值

Laravel 的许多内置错误消息都包含一个 `:attribute` 占位符，该占位符会被替换为正在验证的字段或属性名称。要自定义用于替换特定字段这些占位符的值，你可以将自定义属性数组作为第四个参数传递给 `Validator::make` 方法：

```php
$validator = Validator::make($input, $rules, $messages, [
    'email' => 'email address',
]);
```

<a name="performing-additional-validation"></a>
### 执行额外验证

有时，你需要在初始验证完成后执行额外的验证。你可以使用验证器的 `after` 方法来实现这一点。`after` 方法接受一个闭包或一个可调用对象数组，这些内容会在验证完成后被调用。给定的可调用对象会接收一个 `Illuminate\Validation\Validator` 实例，使你可以在必要时添加额外的错误消息：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make(/* ... */);

$validator->after(function ($validator) {
    if ($this->somethingElseIsInvalid()) {
        $validator->errors()->add(
            'field', 'Something is wrong with this field!'
        );
    }
});

if ($validator->fails()) {
    // ...
}
```

如前所述，`after` 方法也接受一个可调用对象数组。如果你的“验证后”逻辑被封装在可调用类中，这种方式尤其方便，这些类会通过它们的 `__invoke` 方法接收一个 `Illuminate\Validation\Validator` 实例：

```php
use App\Validation\ValidateShippingTime;
use App\Validation\ValidateUserStatus;

$validator->after([
    new ValidateUserStatus,
    new ValidateShippingTime,
    function ($validator) {
        // ...
    },
]);
```

<a name="working-with-validated-input"></a>
## 使用已验证的输入

在使用表单请求或手动创建的验证器实例验证传入的请求数据后，你可能希望获取实际经过验证的传入请求数据。这可以通过多种方式实现。首先，你可以在表单请求或验证器实例上调用 `validated` 方法。该方法会返回一个包含已验证数据的数组：

```php
$validated = $request->validated();

$validated = $validator->validated();
```

或者，你可以在表单请求或验证器实例上调用 `safe` 方法。该方法会返回一个 `Illuminate\Support\ValidatedInput` 实例。这个对象提供了 `only`、`except` 和 `all` 方法，用于获取已验证数据的子集或完整的已验证数据数组：

```php
$validated = $request->safe()->only(['name', 'email']);

$validated = $request->safe()->except(['name', 'email']);

$validated = $request->safe()->all();
```

此外，`Illuminate\Support\ValidatedInput` 实例可以被遍历，也可以像数组一样进行访问：

```php
// 可以遍历已验证的数据...
foreach ($request->safe() as $key => $value) {
    // ...
}

// 可以像数组一样访问已验证的数据...
$validated = $request->safe();

$email = $validated['email'];
```

如果你希望向已验证的数据中添加额外字段，可以调用 `merge` 方法：

```php
$validated = $request->safe()->merge(['name' => 'Taylor Otwell']);
```

如果你希望以[集合](/docs/{{version}}/collections)实例的形式获取已验证的数据，可以调用 `collect` 方法：

```php
$collection = $request->safe()->collect();
```

<a name="working-with-error-messages"></a>
## 处理错误消息

在 `Validator` 实例上调用 `errors` 方法后，你将获得一个 `Illuminate\Support\MessageBag` 实例，该实例提供了多种用于处理错误消息的便捷方法。自动提供给所有视图的 `$errors` 变量同样也是 `MessageBag` 类的实例。

<a name="retrieving-the-first-error-message-for-a-field"></a>
#### 获取某个字段的第一条错误消息

要获取给定字段的第一条错误消息，可以使用 `first` 方法：

```php
$errors = $validator->errors();

echo $errors->first('email');
```

<a name="retrieving-all-error-messages-for-a-field"></a>
#### 获取某个字段的所有错误消息

如果你需要获取给定字段的所有错误消息数组，可以使用 `get` 方法：

```php
foreach ($errors->get('email') as $message) {
    // ...
}
```

如果你正在验证一个数组表单字段，可以使用 `*` 字符获取数组中每个元素的所有错误消息：

```php
foreach ($errors->get('attachments.*') as $message) {
    // ...
}
```

<a name="retrieving-all-error-messages-for-all-fields"></a>
#### 获取所有字段的所有错误消息

要获取所有字段的所有错误消息数组，请使用 `all` 方法：

```php
foreach ($errors->all() as $message) {
    // ...
}
```

<a name="determining-if-messages-exist-for-a-field"></a>
#### 判断某个字段是否存在错误消息

可以使用 `has` 方法来判断给定字段是否存在任何错误消息：

```php
if ($errors->has('email')) {
    // ...
}
```

<a name="specifying-custom-messages-in-language-files"></a>
### 在语言文件中指定自定义消息

Laravel 的每个内置验证规则都有一条错误消息，这些消息位于应用程序的 `lang/en/validation.php` 文件中。如果你的应用程序没有 `lang` 目录，可以使用 `lang:publish` Artisan 命令让 Laravel 创建它。

在 `lang/en/validation.php` 文件中，你会找到每个验证规则对应的翻译条目。你可以根据应用程序的需求自由更改或修改这些消息。

此外，你可以将此文件复制到其他语言目录中，以便将消息翻译成应用程序所使用的语言。要了解更多关于 Laravel 本地化的信息，请查看完整的[本地化文档](/docs/{{version}}/localization)。

> [!NOTE]
> 默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果你想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

<a name="custom-messages-for-specific-attributes"></a>
#### 针对特定属性的自定义消息

你可以在应用程序的验证语言文件中，自定义指定属性与规则组合所使用的错误消息。为此，请将你的自定义消息添加到应用程序 `lang/xx/validation.php` 语言文件的 `custom` 数组中：

```php
'custom' => [
    'email' => [
        'required' => 'We need to know your email address!',
        'max' => 'Your email address is too long!'
    ],
],
```

<a name="specifying-attribute-in-language-files"></a>
### 在语言文件中指定属性

Laravel 的许多内置错误消息都包含一个 `:attribute` 占位符，该占位符会被替换为正在验证的字段或属性名称。如果你希望验证消息中的 `:attribute` 部分被替换为自定义值，可以在 `lang/xx/validation.php` 语言文件的 `attributes` 数组中指定自定义属性名称：

```php
'attributes' => [
    'email' => 'email address',
],
```

> [!NOTE]
> 默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果你想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

<a name="specifying-values-in-language-files"></a>
### 在语言文件中指定值

Laravel 的一些内置验证规则错误消息中包含一个 `:value` 占位符，该占位符会被替换为请求属性的当前值。不过，有时你可能需要将验证消息中的 `:value` 部分替换为该值的自定义表示形式。例如，考虑以下规则，它指定当 `payment_type` 的值为 `cc` 时，必须提供信用卡号码：

```php
Validator::make($request->all(), [
    'credit_card_number' => ['required_if:payment_type,cc']
]);
```

如果该验证规则失败，将生成以下错误消息：

```text
The credit card number field is required when payment type is cc.
```

你可以不将 `cc` 显示为支付类型的值，而是在 `lang/xx/validation.php` 语言文件中通过定义一个 `values` 数组，指定一个更友好的值表示形式：

```php
'values' => [
    'payment_type' => [
        'cc' => 'credit card'
    ],
],
```

> [!NOTE]
> 默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果你想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

定义此值后，验证规则将生成以下错误消息：

```text
The credit card number field is required when payment type is credit card.
```

<a name="available-validation-rules"></a>
## 可用的验证规则

下面列出了所有可用的验证规则及其功能：

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

#### 布尔值

<div class="collection-method-list" markdown="1">

[已接受](#rule-accepted)
[条件接受](#rule-accepted-if)
[布尔值](#rule-boolean)
[已拒绝](#rule-declined)
[条件拒绝](#rule-declined-if)

</div>

#### 字符串

<div class="collection-method-list" markdown="1">

[有效 URL](#rule-active-url)
[字母](#rule-alpha)
[字母、数字、短横线和下划线](#rule-alpha-dash)
[字母和数字](#rule-alpha-num)
[ASCII](#rule-ascii)
[确认](#rule-confirmed)
[当前密码](#rule-current-password)
[不同](#rule-different)
[不能以指定值开头](#rule-doesnt-start-with)
[不能以指定值结尾](#rule-doesnt-end-with)
[电子邮件](#rule-email)
[以指定值结尾](#rule-ends-with)
[枚举](#rule-enum)
[十六进制颜色](#rule-hex-color)
[在指定值中](#rule-in)
[IP 地址](#rule-ip)
[JSON](#rule-json)
[小写](#rule-lowercase)
[MAC 地址](#rule-mac)
[最大值](#rule-max)
[最小值](#rule-min)
[不在指定值中](#rule-not-in)
[正则表达式](#rule-regex)
[非正则表达式](#rule-not-regex)
[相同](#rule-same)
[大小](#rule-size)
[以指定值开头](#rule-starts-with)
[字符串](#rule-string)
[大写](#rule-uppercase)
[URL](#rule-url)
[ULID](#rule-ulid)
[UUID](#rule-uuid)

</div>

#### 数字

<div class="collection-method-list" markdown="1">

[介于](#rule-between)
[小数](#rule-decimal)
[不同](#rule-different)
[位数](#rule-digits)
[位数范围](#rule-digits-between)
[大于](#rule-gt)
[大于或等于](#rule-gte)
[整数](#rule-integer)
[小于](#rule-lt)
[小于或等于](#rule-lte)
[最大值](#rule-max)
[最大位数](#rule-max-digits)
[最小值](#rule-min)
[最小位数](#rule-min-digits)
[倍数](#rule-multiple-of)
[数值](#rule-numeric)
[相同](#rule-same)
[大小](#rule-size)

</div>

#### 数组

<div class="collection-method-list" markdown="1">

[数组](#rule-array)
[数组键](#rule-array-keys)
[介于](#rule-between)
[包含](#rule-contains)
[不包含](#rule-doesnt-contain)
[不同](#rule-distinct)
[在数组中](#rule-in-array)
[在数组键中](#rule-in-array-keys)
[列表](#rule-list)
[最大值](#rule-max)
[最小值](#rule-min)
[大小](#rule-size)

</div>

#### 日期

<div class="collection-method-list" markdown="1">

[之后](#rule-after)
[之后或等于](#rule-after-or-equal)
[之前](#rule-before)
[之前或等于](#rule-before-or-equal)
[日期](#rule-date)
[日期相等](#rule-date-equals)
[日期格式](#rule-date-format)
[不同](#rule-different)
[时区](#rule-timezone)

</div>

#### 文件

<div class="collection-method-list" markdown="1">

[介于](#rule-between)
[尺寸](#rule-dimensions)
[编码](#rule-encoding)
[扩展名](#rule-extensions)
[文件](#rule-file)
[图像](#rule-image)
[最大值](#rule-max)
[最小值](#rule-min)
[MIME 类型](#rule-mimetypes)
[通过文件扩展名判断 MIME 类型](#rule-mimes)
[大小](#rule-size)

</div>

#### 数据库

<div class="collection-method-list" markdown="1">

[存在](#rule-exists)
[唯一](#rule-unique)

</div>

#### 实用工具

<div class="collection-method-list" markdown="1">

[任意一个](#rule-anyof)
[遇错即停](#rule-bail)
[排除](#rule-exclude)
[条件排除](#rule-exclude-if)
[除非满足条件否则排除](#rule-exclude-unless)
[与指定字段同时存在时排除](#rule-exclude-with)
[缺少指定字段时排除](#rule-exclude-without)
[已填写](#rule-filled)
[缺失](#rule-missing)
[条件缺失](#rule-missing-if)
[除非满足条件否则缺失](#rule-missing-unless)
[与指定字段同时存在时缺失](#rule-missing-with)
[与所有指定字段同时存在时缺失](#rule-missing-with-all)
[可为空](#rule-nullable)
[存在](#rule-present)
[条件存在](#rule-present-if)
[除非满足条件否则存在](#rule-present-unless)
[与指定字段同时存在时存在](#rule-present-with)
[与所有指定字段同时存在时存在](#rule-present-with-all)
[禁止](#rule-prohibited)
[条件禁止](#rule-prohibited-if)
[条件接受时禁止](#rule-prohibited-if-accepted)
[条件拒绝时禁止](#rule-prohibited-if-declined)
[除非满足条件否则禁止](#rule-prohibited-unless)
[禁止其他字段](#rule-prohibits)
[必填](#rule-required)
[条件必填](#rule-required-if)
[条件接受时必填](#rule-required-if-accepted)
[条件拒绝时必填](#rule-required-if-declined)
[除非满足条件否则必填](#rule-required-unless)
[与指定字段同时存在时必填](#rule-required-with)
[与所有指定字段同时存在时必填](#rule-required-with-all)
[缺少指定字段时必填](#rule-required-without)
[缺少所有指定字段时必填](#rule-required-without-all)
[必需的数组键](#rule-required-array-keys)
[有时](#validating-when-present)

</div>

<a name="rule-builders"></a>
### 规则构建器

除了使用字符串外，许多验证规则还可以通过 `Illuminate\Validation\Rule` 类上的方法定义。这些方法支持 IDE 自动补全，并且可以与字符串规则结合使用：

```php
use Illuminate\Validation\Rule;

'name' => [Rule::required(), Rule::string()->max(255)],
'terms' => [Rule::accepted()],
'enabled' => [Rule::boolean()],
'website' => [Rule::nullable(), Rule::activeUrl()],
```

方法名称使用驼峰式命名，例如 `Rule::hexColor()`、`Rule::macAddress()` 和 `Rule::requiredArrayKeys(['name', 'email'])`。依赖其他字段的规则接受字段名称或比较值作为参数：

```php
'terms' => [Rule::acceptedIf('account_type', ['personal', 'business'])],
'nickname' => [Rule::excludeWith('name')],
'email' => [Rule::requiredWithout(['phone', 'mobile'])],
'settings' => [Rule::presentIf('account_type', 'business')],
```

`acceptedIf`、`declinedIf`、`missingIf`、`missingUnless`、`presentIf` 和 `presentUnless` 方法接受单个比较值或比较值数组。`requiredWith`、`requiredWithAll`、`requiredWithout`、`requiredWithoutAll`、`missingWith`、`missingWithAll`、`presentWith`、`presentWithAll` 和 `prohibits` 等方法接受字段名称数组或多个字段名称参数。

正则表达式也可以使用 `regex` 和 `notRegex` 方法定义：

```php
'username' => [Rule::required(), Rule::regex('/^[a-z]+$/i')],
'code' => [Rule::notRegex('/^test-/i')],
```

<a name="rule-accepted"></a>
#### accepted

正在验证的字段必须为 `"yes"`、`"on"`、`1`、`"1"`、`true` 或 `"true"`。这对于验证“服务条款”的接受情况或类似字段非常有用。

<a name="rule-accepted-if"></a>
#### accepted_if:anotherfield,value,...

如果另一个正在验证的字段等于指定值，则当前正在验证的字段必须为 `"yes"`、`"on"`、`1`、`"1"`、`true` 或 `"true"`。这对于验证“服务条款”的接受情况或类似字段非常有用。

<a name="rule-active-url"></a>
#### active_url

根据 PHP 的 `dns_get_record` 函数，正在验证的字段必须具有有效的 A 或 AAAA 记录。在将提供的 URL 传递给 `dns_get_record` 之前，会先使用 PHP 的 `parse_url` 函数提取其主机名。

测试执行 DNS 查询的验证规则（例如 `active_url` 和 `email:dns`）时，可以使用 `Validator::fakeDnsLookups` 方法。该方法会模拟 DNS 查询，同时保留规则的其他验证行为：

```php
use Illuminate\Support\Facades\Validator;

Validator::fakeDnsLookups();
```

<a name="rule-after"></a>
#### after:_date_

正在验证的字段必须是晚于给定日期的值。日期会被传递给 PHP 的 `strtotime` 函数，以转换为有效的 `DateTime` 实例：

```php
'start_date' => ['required', 'date', 'after:tomorrow']
```

除了传递一个由 `strtotime` 解析的日期字符串之外，你还可以指定另一个字段，与该日期进行比较：

```php
'finish_date' => ['required', 'date', 'after:start_date']
```

为方便起见，可以使用流式的 `date` 规则构建器来构建基于日期的规则：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->after(today()->addDays(7)),
],
```

`afterToday` 和 `todayOrAfter` 方法可用于以流式方式分别表示日期必须晚于今天，或等于今天或晚于今天：

```php
'start_date' => [
    'required',
    Rule::date()->afterToday(),
],
```

<a name="rule-after-or-equal"></a>
#### after\_or\_equal:_date_

正在验证的字段必须是晚于或等于给定日期的值。有关更多信息，请参阅 [after](#rule-after) 规则。

为方便起见，可以使用流式的 `date` 规则构建器来构建基于日期的规则：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->afterOrEqual(today()->addDays(7)),
],
```

<a name="rule-anyof"></a>
#### anyOf

`Rule::anyOf` 验证规则允许你指定正在验证的字段必须满足给定验证规则集中的任意一个。例如，下面的规则将验证 `username` 字段要么是一个电子邮件地址，要么是一个至少 6 个字符长的字母数字字符串（包括短横线）：

```php
use Illuminate\Validation\Rule;

'username' => [
    'required',
    Rule::anyOf([
        ['string', 'email'],
        ['string', 'alpha_dash', 'min:6'],
    ]),
],
```

<a name="rule-alpha"></a>
#### alpha

正在验证的字段必须完全由 Unicode 字母字符组成，这些字符包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=) 和 [\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=) 中。

要将此验证规则限制为 ASCII 范围内的字符（`a-z` 和 `A-Z`），可以向验证规则提供 `ascii` 选项：

```php
'username' => ['alpha:ascii'],
```

<a name="rule-alpha-dash"></a>
#### alpha_dash

正在验证的字段必须完全由 Unicode 字母数字字符组成，这些字符包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=)、[\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=)、[\p{N}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AN%3A%5D&g=&i=) 中，以及 ASCII 短横线（`-`）和 ASCII 下划线（`_`）。

要将此验证规则限制为 ASCII 范围内的字符（`a-z`、`A-Z` 和 `0-9`），可以向验证规则提供 `ascii` 选项：

```php
'username' => ['alpha_dash:ascii'],
```

<a name="rule-alpha-num"></a>
#### alpha_num

正在验证的字段必须完全由 Unicode 字母数字字符组成，这些字符包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=)、[\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=) 和 [\p{N}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AN%3A%5D&g=&i=) 中。

要将此验证规则限制为 ASCII 范围内的字符（`a-z`、`A-Z` 和 `0-9`），可以向验证规则提供 `ascii` 选项：

```php
'username' => ['alpha_num:ascii'],
```

<a name="rule-array"></a>
#### array

正在验证的字段必须是一个 PHP `array`。

当向 `array` 规则提供额外值时，输入数组中的每个键都必须存在于提供给该规则的值列表中。在下面的示例中，输入数组中的 `admin` 键是无效的，因为它不包含在提供给 `array` 规则的值列表中：

```php
use Illuminate\Support\Facades\Validator;

$input = [
    'user' => [
        'name' => 'Taylor Otwell',
        'username' => 'taylorotwell',
        'admin' => true,
    ],
];

Validator::make($input, [
    'user' => ['array:name,username'],
]);
```

一般来说，你应该始终指定允许存在于数组中的数组键。

<a name="rule-array-keys"></a>
#### array_keys:_foo_,_bar_,...

待验证字段必须是 PHP `array`，且其键必须全部包含在给定列表中。至少需要提供一个键：

```php
'user' => ['array_keys:name,username'],
```

为方便起见，可以使用 `Rule::arrayKeys` 方法：

```php
'user' => [Rule::arrayKeys('name', 'username')],
```

<a name="rule-ascii"></a>
#### ascii

正在验证的字段必须完全由 7 位 ASCII 字符组成。

<a name="rule-bail"></a>
#### bail

在第一次验证失败后，停止运行该字段的验证规则。

虽然 `bail` 规则只会在遇到验证失败时停止验证特定字段，但 `stopOnFirstFailure` 方法会通知验证器，一旦发生一次验证失败，就停止验证所有属性：

```php
if ($validator->stopOnFirstFailure()->fails()) {
    // ...
}
```

<a name="rule-before"></a>
#### before:_date_

正在验证的字段必须是早于给定日期的值。日期会被传递给 PHP 的 `strtotime` 函数，以转换为有效的 `DateTime` 实例。此外，与 [after](#rule-after) 规则一样，也可以将另一个正在验证的字段名称作为 `date` 的值。

为方便起见，基于日期的规则也可以使用流式的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->before(today()->subDays(7)),
],
```

`beforeToday` 和 `todayOrBefore` 方法可以分别以流式方式表示日期必须早于今天，或等于今天或早于今天：

```php
'start_date' => [
    'required',
    Rule::date()->beforeToday(),
],
```

<a name="rule-before-or-equal"></a>
#### before\_or\_equal:_date_

正在验证的字段必须是早于或等于给定日期的值。日期会被传递给 PHP 的 `strtotime` 函数，以转换为有效的 `DateTime` 实例。此外，与 [after](#rule-after) 规则一样，也可以将另一个正在验证的字段名称作为 `date` 的值。

为方便起见，基于日期的规则也可以使用流式的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->beforeOrEqual(today()->subDays(7)),
],
```

<a name="rule-between"></a>
#### between:_min_,_max_

正在验证的字段大小必须介于给定的 *min* 和 *max* 之间（包含边界值）。字符串、数值、数组和文件的判断方式与 [size](#rule-size) 规则相同。

<a name="rule-boolean"></a>
#### boolean

正在验证的字段必须能够转换为布尔值。可接受的输入包括 `true`、`false`、`1`、`0`、`"1"` 和 `"0"`。

你可以使用 `strict` 参数，使字段只有在其值为 `true` 或 `false` 时才被视为有效：

```php
'foo' => ['boolean:strict']
```

你也可以使用 `Rule::boolean` 方法，传入 `true` 以启用严格验证：

```php
'foo' => [Rule::boolean(true)],
```

<a name="rule-confirmed"></a>
#### confirmed

正在验证的字段必须存在一个与之匹配的 `{field}_confirmation` 字段。例如，如果正在验证的字段是 `password`，那么输入中必须存在一个与其匹配的 `password_confirmation` 字段。

你也可以传入一个自定义的确认字段名称。例如，`confirmed:repeat_username` 将要求 `repeat_username` 字段与正在验证的字段相匹配。

你也可以使用 `Rule::confirmed` 方法，通过 `customField` 方法指定自定义确认字段：

```php
'username' => [Rule::confirmed()->customField('repeat_username')],
```

<a name="rule-contains"></a>
#### contains:_foo_,_bar_,...

正在验证的字段必须是一个数组，并且包含所有给定的参数值。由于此规则通常需要你对数组使用 `implode`，因此可以使用 `Rule::contains` 方法以流式方式构建该规则：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'roles' => [
        'required',
        'array',
        Rule::contains(['admin', 'editor']),
    ],
]);
```

<a name="rule-doesnt-contain"></a>
#### doesnt_contain:_foo_,_bar_,...

正在验证的字段必须是一个数组，并且不包含任何给定的参数值。由于此规则通常需要你对数组使用 `implode`，因此可以使用 `Rule::doesntContain` 方法以流式方式构建该规则：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'roles' => [
        'required',
        'array',
        Rule::doesntContain(['admin', 'editor']),
    ],
]);
```

<a name="rule-current-password"></a>
#### current_password

正在验证的字段必须与已认证用户的密码匹配。你可以使用该规则的第一个参数指定一个[身份验证守卫](/docs/{{version}}/authentication)：

```php
'password' => ['current_password:api']
```

你也可以使用 `Rule::currentPassword` 方法，并通过 `guard` 方法指定认证 guard：

```php
'password' => [Rule::currentPassword()->guard('api')],
```

<a name="rule-date"></a>
#### date

根据 PHP 的 `strtotime` 函数，正在验证的字段必须是一个有效的、非相对日期。

<a name="rule-date-equals"></a>
#### date_equals:_date_

正在验证的字段必须等于给定日期。日期会被传递给 PHP 的 `strtotime` 函数，以转换为有效的 `DateTime` 实例。

为方便起见，可以使用流畅的 `date` 规则构建器来构建基于日期的规则：

```php
use Illuminate\Validation\Rule;

'start_date' => [Rule::date()->equals('2026-01-01')],
```

`equals` 方法接受日期字符串、`DateTimeInterface` 实例或要比较的另一个字段的名称。

<a name="rule-date-format"></a>
#### date_format:_format_,...

正在验证的字段必须匹配给定的 *formats* 中的一个。验证字段时，你应该使用 `date` 或 `date_format`，而不是同时使用两者。此验证规则支持 PHP [DateTime](https://www.php.net/manual/en/class.datetime.php) 类支持的所有格式。

为方便起见，可以使用流式的 `date` 规则构建器来构建基于日期的规则：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->format('Y-m-d'),
],
```

<a name="rule-decimal"></a>
#### decimal:_min_,_max_

正在验证的字段必须是数值，并且必须包含指定数量的小数位：

```php
// 必须恰好有两位小数（9.99）...
'price' => ['decimal:2']

// 必须有 2 到 4 位小数...
'price' => ['decimal:2,4']
```

<a name="rule-declined"></a>
#### declined

正在验证的字段必须为 `"no"`、`"off"`、`0`、`"0"`、`false` 或 `"false"`。

<a name="rule-declined-if"></a>
#### declined_if:anotherfield,value,...

如果另一个正在验证的字段等于指定值，则当前正在验证的字段必须为 `"no"`、`"off"`、`0`、`"0"`、`false` 或 `"false"`。

<a name="rule-different"></a>
#### different:_field_

正在验证的字段必须具有与 *field* 不同的值。

<a name="rule-digits"></a>
#### digits:_value_

正在验证的整数长度必须恰好为 *value*。

<a name="rule-digits-between"></a>
#### digits_between:_min_,_max_

正在验证的整数长度必须介于给定的 *min* 和 *max* 之间。

<a name="rule-dimensions"></a>
#### dimensions

正在验证的文件必须是符合该规则参数所指定尺寸约束的图像：

```php
'avatar' => ['dimensions:min_width=100,min_height=200']
```

可用的约束包括：*min_width*、*max_width*、*min_height*、*max_height*、*width*、*height*、*ratio*、*min_ratio*、*max_ratio*。

*ratio* 约束应表示为宽度除以高度。它既可以指定为类似 `3/2` 的分数，也可以指定为类似 `1.5` 的浮点数：

```php
'avatar' => ['dimensions:ratio=3/2']
```

*min_ratio* 和 *max_ratio* 约束可用于定义可接受的宽高比范围：

```php
'avatar' => ['dimensions:min_ratio=1/2,max_ratio=3/2']
```

由于此规则需要多个参数，因此通常使用 `Rule::dimensions` 方法以流式方式构建该规则会更加方便：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'avatar' => [
        'required',
        Rule::dimensions()
            ->maxWidth(1000)
            ->maxHeight(500)
            ->ratio(3 / 2),
    ],
]);
```

你也可以使用 `minRatio`、`maxRatio` 和 `ratioBetween` 方法，以流式方式定义宽高比约束：

```php
Rule::dimensions()->ratioBetween(min: 1 / 2, max: 3 / 2);
```

<a name="rule-distinct"></a>
#### distinct

验证数组时，正在验证的字段不得包含任何重复值：

```php
'foo.*.id' => ['distinct']
```

默认情况下，`distinct` 使用宽松的变量比较。要使用严格比较，可以在验证规则定义中添加 `strict` 参数：

```php
'foo.*.id' => ['distinct:strict']
```

你可以在验证规则的参数中添加 `ignore_case`，使该规则忽略大小写差异：

```php
'foo.*.id' => ['distinct:ignore_case']
```

你也可以使用 `Rule::distinct` 方法，根据需要链式调用 `strict` 和 `ignoreCase` 方法：

```php
'foo.*.id' => [Rule::distinct()->strict()->ignoreCase()],
```

<a name="rule-doesnt-start-with"></a>
#### doesnt_start_with:_foo_,_bar_,...

正在验证的字段不能以给定值中的任何一个开头。

<a name="rule-doesnt-end-with"></a>
#### doesnt_end_with:_foo_,_bar_,...

正在验证的字段不能以给定值中的任何一个结尾。

<a name="rule-email"></a>
#### email

正在验证的字段必须符合电子邮件地址的格式。此验证规则使用 [egulias/email-validator](https://github.com/egulias/EmailValidator) 包来验证电子邮件地址。默认情况下，会应用 `RFCValidation` 验证器，但你也可以应用其他验证方式：

```php
'email' => ['email:rfc,dns']
```

上面的示例将应用 `RFCValidation` 和 `DNSCheckValidation` 验证。下面是你可以应用的完整验证方式列表：

<div class="content-list" markdown="1">

-   `rfc`：`RFCValidation` - 根据[支持的 RFC](https://github.com/egulias/EmailValidator?tab=readme-ov-file#supported-rfcs)验证电子邮件地址。
-   `strict`：`NoRFCWarningsValidation` - 根据[支持的 RFC](https://github.com/egulias/EmailValidator?tab=readme-ov-file#supported-rfcs)验证电子邮件地址，当发现警告时验证失败（例如末尾句点和多个连续句点）。
-   `dns`：`DNSCheckValidation` - 确保电子邮件地址的域名具有有效的 MX 记录。
-   `spoof`：`SpoofCheckValidation` - 确保电子邮件地址不包含同形异义字符或具有欺骗性的 Unicode 字符。
-   `filter`：`FilterEmailValidation` - 确保根据 PHP 的 `filter_var` 函数，该电子邮件地址有效。
-   `filter_unicode`：`FilterEmailValidation::unicode()` - 确保根据 PHP 的 `filter_var` 函数，该电子邮件地址有效，并允许某些 Unicode 字符。

</div>

为方便起见，可以使用流式规则构建器来构建电子邮件验证规则：

```php
use Illuminate\Validation\Rule;

$request->validate([
    'email' => [
        'required',
        Rule::email()
            ->rfcCompliant(strict: false)
            ->validateMxRecord()
            ->preventSpoofing()
    ],
]);
```

`dns` 验证器会执行真实的 DNS 查询，以确认地址的域名具有有效的 MX 记录。它不会判断单个邮箱是否存在。

由于测试不应依赖实时 DNS 查询，可以使用 `Validator::fakeDnsLookups` 方法 [模拟 DNS 查询](#rule-active-url)，同时继续执行其他指定的验证，例如 `rfc`：

```php
use Illuminate\Support\Facades\Validator;

Validator::fakeDnsLookups();
```

这样，应用就可以在测试时继续使用现有的验证规则：

```php
'email' => ['required', 'email:rfc,dns'],
```

> [!WARNING]
> `dns` 和 `spoof` 验证器需要 PHP 的 `intl` 扩展。

<a name="rule-encoding"></a>
#### encoding:*encoding_type*

正在验证的字段必须匹配指定的字符编码。此规则使用 PHP 的 `mb_check_encoding` 函数来验证给定文件或字符串值的编码。为方便起见，可以使用 Laravel 的流式文件规则构建器来构建 `encoding` 规则：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rules\File;

Validator::validate($input, [
    'attachment' => [
        'required',
        File::types(['csv'])
            ->encoding('utf-8'),
    ],
]);
```

<a name="rule-ends-with"></a>
#### ends_with:_foo_,_bar_,...

正在验证的字段必须以给定值中的一个结尾。

<a name="rule-enum"></a>
#### enum

`Enum` 规则是一个基于类的规则，用于验证正在验证的字段是否包含有效的枚举值。`Enum` 规则只接受枚举名称作为其构造函数参数。在验证原始值时，应向 `Enum` 规则提供一个有支持值的枚举：

```php
use App\Enums\ServerStatus;
use Illuminate\Validation\Rule;

$request->validate([
    'status' => [Rule::enum(ServerStatus::class)],
]);
```

`Enum` 规则的 `only` 和 `except` 方法可用于限制哪些枚举项应被视为有效：

```php
Rule::enum(ServerStatus::class)
    ->only([ServerStatus::Pending, ServerStatus::Active]);

Rule::enum(ServerStatus::class)
    ->except([ServerStatus::Pending, ServerStatus::Active]);
```

`when` 方法可用于有条件地修改 `Enum` 规则：

```php
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\Rule;

Rule::enum(ServerStatus::class)
    ->when(
        Auth::user()->isAdmin(),
        fn ($rule) => $rule->only(...),
        fn ($rule) => $rule->only(...),
    );
```

<a name="rule-exclude"></a>
#### exclude

正在验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

<a name="rule-exclude-if"></a>
#### exclude_if:_anotherfield_,_value_

如果 *anotherfield* 字段等于 *value*，正在验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

如果需要复杂的条件排除逻辑，可以使用 `Rule::excludeIf` 方法。该方法接受一个布尔值或一个闭包。当传入闭包时，闭包应返回 `true` 或 `false`，以指示是否应排除正在验证的字段：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::excludeIf($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::excludeIf(fn () => $request->user()->is_admin)],
]);
```

<a name="rule-exclude-unless"></a>
#### exclude_unless:_anotherfield_,_value_

除非 *anotherfield* 字段等于 *value*，否则正在验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。如果 *value* 为 `null`（`exclude_unless:name,null`），则除非用于比较的字段为 `null`，或者该比较字段不存在于请求数据中，否则正在验证的字段将被排除。

如果需要复杂的条件排除逻辑，可以使用 `Rule::excludeUnless` 方法。该方法接受一个布尔值或一个闭包。当传入闭包时，闭包应返回 `true` 或 `false`，以指示正在验证的字段是否不应被排除：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::excludeUnless($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::excludeUnless(fn () => $request->user()->is_admin)],
]);
```

<a name="rule-exclude-with"></a>
#### exclude_with:_anotherfield_

如果 *anotherfield* 字段存在，正在验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

<a name="rule-exclude-without"></a>
#### exclude_without:_anotherfield_

如果 *anotherfield* 字段不存在，正在验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

<a name="rule-exists"></a>
#### exists:_table_,_column_

正在验证的字段必须存在于给定的数据库表中。

<a name="basic-usage-of-exists-rule"></a>
#### Exists 规则的基本用法

```php
'state' => ['exists:states']
```

如果未指定 `column` 选项，则会使用字段名称。因此，在这种情况下，该规则将验证 `states` 数据库表中是否存在一条记录，其 `state` 列的值与请求中的 `state` 属性值相匹配。

<a name="specifying-a-custom-column-name"></a>
#### 指定自定义列名

你可以通过将数据库列名放在数据库表名之后，明确指定验证规则应使用的数据库列名：

```php
'state' => ['exists:states,abbreviation']
```

有时，你可能需要为 `exists` 查询指定特定的数据库连接。你可以通过在表名前加上连接名称来实现：

```php
'email' => ['exists:connection.staff,email']
```

除了直接指定表名之外，你还可以指定 Eloquent 模型，由该模型来确定表名：

```php
'user_id' => ['exists:App\Models\User,id']
```

如果你想自定义验证规则所执行的查询，可以使用 `Rule` 类以流式方式定义该规则。

```php
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'email' => [
        'required',
        Rule::exists('staff')->where(function (Builder $query) {
            $query->where('account_id', 1);
        }),
    ],
]);
```

你可以通过向 `exists` 方法提供第二个参数（列名），显式指定由 `Rule::exists` 方法生成的 `exists` 规则应使用的数据库列名：

```php
'state' => [Rule::exists('states', 'abbreviation')],
```

有时，你可能希望验证一个值数组中的所有值是否都存在于数据库中。你可以通过同时为被验证字段添加 `exists` 规则和 [array](#rule-array) 规则来实现：

```php
'states' => ['array', Rule::exists('states', 'abbreviation')],
```

当这两个规则同时分配给一个字段时，Laravel 会自动构建一条查询，以确定所有给定的值是否都存在于指定的数据表中。

<a name="rule-extensions"></a>
#### extensions:_foo_,_bar_,...

被验证的文件必须具有用户指定的扩展名，并且该扩展名必须与列出的扩展名之一对应：

```php
'photo' => ['required', 'extensions:jpg,png'],
```

> [!WARNING]
> 你绝不应该仅依赖用户指定的文件扩展名来验证文件。通常应始终将此规则与 [mimes](#rule-mimes) 或 [mimetypes](#rule-mimetypes) 规则结合使用。

<a name="rule-file"></a>
#### file

被验证的字段必须是一个成功上传的文件。

<a name="rule-filled"></a>
#### filled

如果被验证的字段存在，则该字段不能为空。

<a name="rule-gt"></a>
#### gt:_field_

被验证的字段必须大于给定的 *field* 或 *value*。两个字段必须具有相同的类型。字符串、数值、数组和文件的计算方式与 [size](#rule-size) 规则所采用的约定相同。

<a name="rule-gte"></a>
#### gte:_field_

被验证的字段必须大于或等于给定的 *field* 或 *value*。两个字段必须具有相同的类型。字符串、数值、数组和文件的比较方式与 [size](#rule-size) 规则所采用的约定相同。

<a name="rule-hex-color"></a>
#### hex_color

被验证的字段必须包含有效的[十六进制](https://developer.mozilla.org/en-US/docs/Web/CSS/hex-color)格式颜色值。

<a name="rule-image"></a>
#### image

待验证文件必须是图片（jpg、jpeg、png、bmp、gif、webp、avif、heic 或 heif）。

> [!WARNING]
> 默认情况下，由于可能存在 XSS 漏洞，`image` 规则不允许 SVG 文件。如果需要允许 SVG 文件，可以向 `image` 规则提供 `allow_svg` 指令（`image:allow_svg`）。

<a name="rule-in"></a>
#### in:_foo_,_bar_,...

被验证的字段必须包含在给定的值列表中。由于此规则通常需要你对数组使用 `implode`，因此可以使用 `Rule::in` 方法以流畅的方式构建该规则：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'zones' => [
        'required',
        Rule::in(['first-zone', 'second-zone']),
    ],
]);
```

当 `in` 规则与 `array` 规则结合使用时，输入数组中的每个值都必须存在于提供给 `in` 规则的值列表中。在下面的示例中，输入数组中的 `LAS` 机场代码是无效的，因为它不包含在提供给 `in` 规则的机场列表中：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

$input = [
    'airports' => ['NYC', 'LAS'],
];

Validator::make($input, [
    'airports' => [
        'required',
        'array',
    ],
    'airports.*' => Rule::in(['NYC', 'LIT']),
]);
```

<a name="rule-in-array"></a>
#### in_array:_anotherfield_.*

被验证的字段必须存在于 *anotherfield* 的值中。

<a name="rule-in-array-keys"></a>
#### in_array_keys:_value_.*

被验证的字段必须是一个数组，并且该数组必须至少包含一个给定的 *values* 作为键：

```php
'config' => ['array', 'in_array_keys:timezone']
```

<a name="rule-integer"></a>
#### integer

被验证的字段必须是整数。

你可以使用 `strict` 参数，仅当字段的类型为 `integer` 时才认为验证通过。具有整数值的字符串将被视为无效：

```php
'age' => ['integer:strict']
```

> [!WARNING]
> 此验证规则不会验证输入是否为 `"integer"` 变量类型，它只会验证输入是否属于 PHP 的 `FILTER_VALIDATE_INT` 规则所接受的类型。如果你需要验证输入是否为数值，请将此规则与 [`numeric` 验证规则](#rule-numeric) 结合使用。

<a name="rule-ip"></a>
#### ip

被验证的字段必须是一个 IP 地址。

你也可以使用 `Rule::ip` 方法，并可选择将 IP 版本限制为 `4` 或 `6`：

```php
'ip_address' => [Rule::ip()],
'ipv4_address' => [Rule::ip()->version(4)],
'ipv6_address' => [Rule::ip()->version(6)],
```

<a name="ipv4"></a>
#### ipv4

被验证的字段必须是一个 IPv4 地址。

<a name="ipv6"></a>
#### ipv6

被验证的字段必须是一个 IPv6 地址。

<a name="rule-json"></a>
#### json

被验证的字段必须是一个有效的 JSON 字符串。

<a name="rule-lt"></a>
#### lt:_field_

被验证的字段必须小于给定的 *field*。两个字段必须具有相同的类型。字符串、数值、数组和文件的比较方式与 [size](#rule-size) 规则所采用的约定相同。

<a name="rule-lte"></a>
#### lte:_field_

被验证的字段必须小于或等于给定的 *field*。两个字段必须具有相同的类型。字符串、数值、数组和文件的比较方式与 [size](#rule-size) 规则所采用的约定相同。

<a name="rule-lowercase"></a>
#### lowercase

被验证的字段必须为小写。

<a name="rule-list"></a>
#### list

被验证的字段必须是一个列表形式的数组。如果数组的键由从 0 到 `count($array) - 1` 的连续数字组成，则该数组被视为列表。

<a name="rule-mac"></a>
#### mac_address

被验证的字段必须是一个 MAC 地址。

<a name="rule-max"></a>
#### max:_value_

被验证的字段必须小于或等于最大值 *value*。字符串、数值、数组和文件的比较方式与 [size](#rule-size) 规则相同。

<a name="rule-max-digits"></a>
#### max_digits:_value_

被验证的整数的最大位数必须为 *value*。

<a name="rule-mimetypes"></a>
#### mimetypes:_text/plain_,...

被验证的文件必须匹配给定的 MIME 类型之一：

```php
'video' => ['mimetypes:video/avi,video/mpeg,video/quicktime'],

'media' => ['mimetypes:image/*,video/*'],
```

为了确定上传文件的 MIME 类型，框架会读取文件内容并尝试推断 MIME 类型，该类型可能与客户端提供的 MIME 类型不同。

<a name="rule-mimes"></a>
#### mimes:_foo_,_bar_,...

被验证的文件必须具有与列出的扩展名之一对应的 MIME 类型：

```php
'photo' => ['mimes:jpg,bmp,png']
```

尽管你只需要指定扩展名，但此规则实际上会通过读取文件内容并推断其 MIME 类型来验证文件的 MIME 类型。MIME 类型及其对应扩展名的完整列表可以在以下位置找到：

[https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types](https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types)

<a name="mime-types-and-extensions"></a>
#### MIME 类型与扩展名

此验证规则不会验证 MIME 类型与用户为文件指定的扩展名是否一致。例如，`mimes:png` 验证规则会将包含有效 PNG 内容的文件视为有效的 PNG 图片，即使该文件名为 `photo.txt`。如果你希望验证用户为文件指定的扩展名，可以使用 [extensions](#rule-extensions) 规则。

> [!WARNING]
> 通过图片验证并不意味着文件以 `.php` 扩展名存储时不会被当作 PHP 执行。以 GIF 或 JPEG 魔数开头的文件，即使包含 PHP 载荷，也可能通过 `mimes:gif` 或 `mimes:jpg` 验证。存储上传文件时，始终使用系统生成的文件名（例如 `hashName()`），并配置 Web 服务器禁止在存储目录内执行 PHP。

<a name="rule-min"></a>
#### min:_value_

被验证的字段必须具有最小值 *value*。字符串、数值、数组和文件的比较方式与 [size](#rule-size) 规则相同。

<a name="rule-min-digits"></a>
#### min_digits:_value_

被验证的整数的最小位数必须为 *value*。

<a name="rule-multiple-of"></a>
#### multiple_of:_value_

被验证的字段必须是 *value* 的倍数。

<a name="rule-missing"></a>
#### missing

被验证的字段不得出现在输入数据中。

<a name="rule-missing-if"></a>
#### missing_if:_anotherfield_,_value_,...

如果 *anotherfield* 字段等于任意一个 *value*，则被验证的字段不得出现在输入数据中。

<a name="rule-missing-unless"></a>
#### missing_unless:_anotherfield_,_value_

除非 *anotherfield* 字段等于任意一个 *value*，否则被验证的字段不得出现在输入数据中。

<a name="rule-missing-with"></a>
#### missing_with:_foo_,_bar_,...

仅当其他指定字段中的任意一个存在时，被验证的字段不得出现。

<a name="rule-missing-with-all"></a>
#### missing_with_all:_foo_,_bar_,...

仅当所有其他指定字段都存在时，被验证的字段不得出现。

<a name="rule-not-in"></a>
#### not_in:_foo_,_bar_,...

被验证的字段不得包含在给定的值列表中。可以使用 `Rule::notIn` 方法以流畅的方式构建该规则：

```php
use Illuminate\Validation\Rule;

Validator::make($data, [
    'toppings' => [
        'required',
        Rule::notIn(['sprinkles', 'cherries']),
    ],
]);
```

<a name="rule-not-regex"></a>
#### not_regex:_pattern_

被验证的字段不得匹配给定的正则表达式。

在内部，此规则使用 PHP 的 `preg_match` 函数。指定的模式应遵循 `preg_match` 所要求的相同格式，因此也必须包含有效的定界符。例如：`'email' => ['not_regex:/^.+$/i']`。

<a name="rule-nullable"></a>
#### nullable

被验证的字段可以为 `null`。

<a name="rule-numeric"></a>
#### numeric

被验证的字段必须是[数值](https://www.php.net/manual/en/function.is-numeric.php)。

你可以使用 `strict` 参数，仅当字段的值为整数或浮点数类型时才认为验证通过。数值字符串将被视为无效：

```php
'amount' => ['numeric:strict']
```

<a name="rule-present"></a>
#### present

被验证的字段必须存在于输入数据中。

<a name="rule-present-if"></a>
#### present_if:_anotherfield_,_value_,...

如果 *anotherfield* 字段等于任意一个 *value*，则被验证的字段必须存在。

<a name="rule-present-unless"></a>
#### present_unless:_anotherfield_,_value_

除非 *anotherfield* 字段等于任意一个 *value*，否则被验证的字段必须存在。

<a name="rule-present-with"></a>
#### present_with:_foo_,_bar_,...

仅当其他指定字段中的任意一个存在时，被验证的字段必须存在。

<a name="rule-present-with-all"></a>
#### present_with_all:_foo_,_bar_,...

仅当所有其他指定字段都存在时，被验证的字段必须存在。

<a name="rule-prohibited"></a>
#### prohibited

被验证的字段必须不存在或为空。如果字段满足以下任一条件，则被视为“空”：

<div class="content-list" markdown="1">

-   值为 `null`。
-   值为空字符串。
-   值为空数组或空的 `Countable` 对象。
-   值为路径为空的已上传文件。

</div>

<a name="rule-prohibited-if"></a>
#### prohibited_if:_anotherfield_,_value_,...

如果 *anotherfield* 字段等于任意一个 *value*，则被验证的字段必须不存在或为空。如果字段满足以下任一条件，则被视为“空”：

<div class="content-list" markdown="1">

-   值为 `null`。
-   值为空字符串。
-   值为空数组或空的 `Countable` 对象。
-   值为路径为空的已上传文件。

</div>

如果需要复杂的条件禁止逻辑，可以使用 `Rule::prohibitedIf` 方法。此方法接受一个布尔值或闭包。当传入闭包时，闭包应返回 `true` 或 `false`，以指示是否应禁止被验证的字段：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::prohibitedIf($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::prohibitedIf(fn () => $request->user()->is_admin)],
]);
```
<a name="rule-prohibited-if-accepted"></a>
#### prohibited_if_accepted:_anotherfield_,...

当 _anotherfield_ 字段的值等于 `"yes"`、 `"on"`、  `1`、  `"1"`、  `true` 或 `"true"`，被验证的字段必须缺失或为空。

<a name="rule-prohibited-if-declined"></a>
#### prohibited_if_declined:_anotherfield_,...

当 _anotherfield_ 字段的值等于 `"no"`、 `"off"`、 `0`、`"0"`、 `false` 或 `"false"` 时，被验证的字段必须缺失或为空。

<a name="rule-prohibited-unless"></a>
#### prohibited_unless:_anotherfield_,_value_,...

除非 _anotherfield_ 字段等于任意指定的 _value_，否则待验证字段必须缺失或为空。如果字段满足以下任一条件，则视为「空」：

<div class="content-list" markdown="1">

- 值为 `null`。
- 值为空字符串。
- 值为空数组或空的 `Countable` 对象。
- 值为一个上传文件且其路径为空。

</div>

如果需要复杂的条件禁用逻辑，你可以使用 `Rule::prohibitedUnless` 方法。该方法接收布尔值或者闭包。传入闭包时，闭包需要返回 `true` 或 `false`，用于标识当前待验证字段是否不应被禁用：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::prohibitedUnless($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::prohibitedUnless(fn () => $request->user()->is_admin)],
]);
```

<a name="rule-prohibits"></a>
#### prohibits:_anotherfield_,...

如果待验证字段存在且不为空，_anotherfield_ 中的所有字段都必须缺失或为空。如果字段满足以下任一条件，则视为「空」：

<div class="content-list" markdown="1">

- 值为 `null`。
- 值为空字符串。
- 值为空数组或空的 `Countable` 对象。
- 值为一个上传文件且其路径为空。

</div>

<a name="rule-regex"></a>
#### regex:_pattern_

待验证字段必须匹配给定的正则表达式。

该规则内部使用 PHP 的 `preg_match` 函数。指定的正则模式需要遵循 `preg_match` 要求的格式，因此必须包含合法的分隔符。示例：`'email' => ['regex:/^.+@.+$/i']`。

<a name="rule-required"></a>
#### required

待验证字段必须存在于输入数据中且不为空。如果字段满足以下任一条件，则视为「空」：

<div class="content-list" markdown="1">

- 值为 `null`。
- 值为空字符串。
- 值为空数组或空的 `Countable` 对象。
- 值为一个上传文件且其路径为空。

</div>

<a name="rule-required-if"></a>
#### required_if:_anotherfield_,_value_,...

如果 _anotherfield_ 等于任意指定值，则待验证字段必须存在且不为空。

如果需要为 `required_if` 规则构造更复杂的条件，可以使用 `Rule::requiredIf` 方法。该方法接收布尔值或者闭包。传入闭包时，闭包需要返回 `true` 或 `false`，用来标识待验证字段是否为必填项：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::requiredIf($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::requiredIf(fn () => $request->user()->is_admin)],
]);
```

<a name="rule-required-if-accepted"></a>
#### required_if_accepted:_anotherfield_,...

如果 _anotherfield_ 字段的值等于 `"yes"`、`"on"`、`1`、`"1"`、`true` 或 `"true"`，则待验证字段必须存在且不为空。

<a name="rule-required-if-declined"></a>
#### required_if_declined:_anotherfield_,...

如果 _anotherfield_ 字段等于 `"no"`、`"off"`、`0`、`"0"`、`false` 或 `"false"`，待验证字段必须存在且不为空。

<a name="rule-required-unless"></a>
#### required_unless:_anotherfield_,_value_,...

除非 _anotherfield_ 字段等于任意指定的 _value_，否则待验证字段必须存在且不为空。这也意味着，除非 _value_ 为 `null`，否则 _anotherfield_ 必须存在于请求数据中。如果 _value_ 为 `null`（`required_unless:name,null`），则除非比较字段为 `null` 或请求数据中缺少该比较字段，否则待验证字段为必填项。

如果需要为 `required_unless` 规则构造更复杂的条件，可以使用 `Rule::requiredUnless` 方法。该方法接受布尔值或闭包；传入闭包时，闭包应返回 `true` 或 `false`，以指示待验证字段是否不是必填项：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => [Rule::requiredUnless($request->user()->is_admin)],
]);

Validator::make($request->all(), [
    'role_id' => [Rule::requiredUnless(fn () => $request->user()->is_admin)],
]);
```

<a name="rule-required-with"></a>
#### required_with:_foo_,_bar_,...

**仅当** 其他指定字段中任意一个存在且不为空时，待验证字段才必须存在且不为空。

<a name="rule-required-with-all"></a>
#### required_with_all:_foo_,_bar_,...

**仅当** 所有其他指定字段都存在且不为空时，待验证字段才必须存在且不为空。

<a name="rule-required-without"></a>
#### required_without:_foo_,_bar_,...

**仅当** 其他指定字段中任意一个为空或不存在时，待验证字段才必须存在且不为空。

<a name="rule-required-without-all"></a>
#### required_without_all:_foo_,_bar_,...

**仅当** 所有其他指定字段都为空或不存在时，待验证字段才必须存在且不为空。

<a name="rule-required-array-keys"></a>
#### required_array_keys:_foo_,_bar_,...

待验证字段必须是数组，且至少包含指定的键。

<a name="rule-same"></a>
#### same:_field_

给定的 _field_ 必须与待验证字段匹配。

<a name="rule-size"></a>
#### size:_value_

待验证字段的大小必须与给定的 _value_ 相匹配。对于字符串，_value_ 对应字符数；对于数值，_value_ 对应指定的整数值（该属性还必须具有 `numeric` 或 `integer` 规则）；对于数组，_size_ 对应数组的 `count`；对于文件，_size_ 对应以千字节为单位的文件大小。下面来看一些示例：

```php
// 验证字符串长度恰好为 12 个字符……
'title' => ['size:12'];

// 验证提供的整数等于 10……
'seats' => ['integer', 'size:10'];

// 验证数组恰好有 5 个元素……
'tags' => ['array', 'size:5'];

// 验证上传文件大小恰好为 512 千字节……
'image' => ['file', 'size:512'];
```

<a name="rule-starts-with"></a>
#### starts_with:_foo_,_bar_,...

待验证字段必须以给定值之一开头。

<a name="rule-string"></a>
#### string

待验证字段必须是字符串。如果还要允许字段为 `null`，应为该字段指定 `nullable` 规则。

为方便起见，字符串验证规则也可以通过流畅的 `Rule::string()` 规则构建器构造：

```php
use Illuminate\Validation\Rule;

'title' => [
    'required',
    Rule::string()
        ->min(3)
        ->max(255)
        ->alphaDash(ascii: true),
],
```

字符串规则构建器为常见字符串约束提供了多种方法，包括 `alpha`、`alphaDash`、`alphaNumeric`、`ascii`、`between`、`doesntEndWith`、`doesntStartWith`、`endsWith`、`exactly`、`lowercase`、`max`、`min`、`startsWith` 和 `uppercase`。由于该规则构建器支持条件操作，你也可以使用 `when` 和 `unless` 方法有条件地应用约束。

<a name="rule-timezone"></a>
#### timezone

待验证字段必须是 `DateTimeZone::listIdentifiers` 方法所定义的有效时区标识符。

此验证规则也可以接收 [`DateTimeZone::listIdentifiers` 方法接受的参数](https://www.php.net/manual/en/datetimezone.listidentifiers.php)：

```php
'timezone' => ['required', 'timezone:all'];

'timezone' => ['required', 'timezone:Africa'];

'timezone' => ['required', 'timezone:per_country,US'];
```

你也可以使用 `Rule::timezone` 方法，将任何 `listIdentifiers` 参数作为数组传入：

```php
'timezone' => [Rule::timezone(['per_country', 'US'])],
```

<a name="rule-unique"></a>
#### unique:_table_,_column_

待验证字段不得存在于给定的数据库表中。

**指定自定义表名 / 列名：**

除了直接指定表名，你还可以指定用于确定表名的 Eloquent 模型：

```php
'email' => ['unique:App\Models\User,email_address']
```

`column` 选项可用于指定字段对应的数据库列。如果未指定 `column` 选项，则使用待验证字段的名称。

```php
'email' => ['unique:users,email_address']
```

**指定自定义数据库连接**

有时，你可能需要为验证器执行的数据库查询设置自定义连接。为此，可以在表名前加上连接名称：

```php
'email' => ['unique:connection.users,email_address']
```

**让唯一性规则忽略指定 ID：**

有时，你可能希望在唯一性验证时忽略指定的 ID。例如，假设「更新个人资料」页面包含用户的姓名、电子邮件地址和所在地。你可能希望确保电子邮件地址唯一，但如果用户只修改姓名而不修改电子邮件地址，就不应因为用户已经拥有该地址而抛出验证错误。

为了让验证器忽略用户的 ID，我们将使用 `Rule` 类以流畅的方式定义规则。

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($data, [
    'email' => [
        'required',
        Rule::unique('users')->ignore($user->id),
    ],
]);
```

> [!WARNING]
> 绝不要将任何用户可控的请求输入传给 `ignore` 方法。你应该只传入系统生成的唯一 ID，例如 Eloquent 模型实例中的自增 ID 或 UUID。否则，应用将容易受到 SQL 注入攻击。

除了将模型键值传给 `ignore` 方法外，也可以传入整个模型实例，Laravel 会自动从模型中提取键：

```php
Rule::unique('users')->ignore($user);
```

如果表使用的主键列名不是 `id`，可以在调用 `ignore` 方法时指定列名：

```php
Rule::unique('users')->ignore($user->id, 'user_id');
```

默认情况下，`unique` 规则会检查与待验证属性同名的列是否唯一。不过，你可以将不同的列名作为第二个参数传给 `unique` 方法：

```php
Rule::unique('users', 'email_address')->ignore($user->id);
```

**添加额外的 Where 子句：**

可以使用 `where` 方法自定义查询，以指定额外的查询条件。例如，下面添加一个查询条件，将搜索范围限定为 `account_id` 列值为 `1` 的记录：

```php
'email' => Rule::unique('users')->where(fn (Builder $query) => $query->where('account_id', 1))
```

**在唯一性检查中忽略软删除记录：**

默认情况下，`unique` 规则在判断唯一性时包含软删除记录。要从唯一性检查中排除软删除记录，可以调用 `withoutTrashed` 方法：

```php
Rule::unique('users')->withoutTrashed();
```

如果模型用于软删除记录的列名不是 `deleted_at`，可以在调用 `withoutTrashed` 方法时传入该列名：

```php
Rule::unique('users')->withoutTrashed('was_deleted_at');
```

<a name="rule-uppercase"></a>
#### uppercase

待验证字段必须为大写。

<a name="rule-url"></a>
#### url

待验证字段必须是有效的 URL。

如果希望指定哪些 URL 协议被视为有效，可以将协议作为验证规则参数传入：

```php
'url' => ['url:http,https'],

'game' => ['url:minecraft,steam'],
```

你也可以使用 `Rule::url` 方法，通过 `protocols` 方法指定允许的协议：

```php
'url' => [Rule::url()->protocols(['http', 'https'])],
```

<a name="rule-ulid"></a>
#### ulid

待验证字段必须是有效的 [通用唯一字典序可排序标识符](https://github.com/ulid/spec)（ULID）。

<a name="rule-uuid"></a>
#### uuid

待验证字段必须是符合 RFC 9562 的有效通用唯一标识符（UUID），版本可以是 1、3、4、5、6、7 或 8。

你也可以验证给定的 UUID 是否符合指定版本的 UUID 规范：

```php
'uuid' => ['uuid:4']
```

你也可以使用 `Rule::uuid` 方法，通过 `version` 方法指定 UUID 版本：

```php
'uuid' => [Rule::uuid()->version(4)],
```

<a name="conditionally-adding-rules"></a>
## 有条件地添加规则

<a name="skipping-validation-when-fields-have-certain-values"></a>
#### 字段具有特定值时跳过验证

有时，如果另一个字段具有给定值，你可能希望不验证某个字段。可以使用 `exclude_if` 验证规则实现。在此示例中，如果 `has_appointment` 字段的值为 `false`，则不会验证 `appointment_date` 和 `doctor_name` 字段：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($data, [
    'has_appointment' => ['required', 'boolean'],
    'appointment_date' => ['exclude_if:has_appointment,false', 'required', 'date'],
    'doctor_name' => ['exclude_if:has_appointment,false', 'required', 'string'],
]);
```

也可以使用 `exclude_unless` 规则，除非另一个字段具有给定值，否则不验证某个字段：

```php
$validator = Validator::make($data, [
    'has_appointment' => ['required', 'boolean'],
    'appointment_date' => ['exclude_unless:has_appointment,true', 'required', 'date'],
    'doctor_name' => ['exclude_unless:has_appointment,true', 'required', 'string'],
]);
```

<a name="validating-when-present"></a>
#### 字段存在时验证

在某些情况下，你可能希望 **仅当** 待验证数据中存在某个字段时才对其运行验证。为此，只需在规则列表中添加 `sometimes` 规则：

```php
$validator = Validator::make($data, [
    'email' => ['sometimes', 'required', 'email'],
]);
```

在上面的示例中，仅当 `$data` 数组中存在 `email` 字段时才会验证该字段。

> [!NOTE]
> 如果要验证一个必须始终存在但可以为空的字段，请参阅 [关于可选字段的说明](#a-note-on-optional-fields)。

<a name="complex-conditional-validation"></a>
#### 复杂条件验证

有时，你可能希望基于更复杂的条件逻辑添加验证规则。例如，仅当另一个字段的值大于 100 时才要求某个字段，或者仅当另一个字段存在时才要求两个字段具有给定值。添加这些规则并不困难。首先，使用永不改变的 _静态规则_ 创建一个 `Validator` 实例：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($request->all(), [
    'email' => ['required', 'email'],
    'games' => ['required', 'integer', 'min:0'],
]);
```

假设我们的 Web 应用面向游戏收藏者。如果有收藏者注册应用且拥有超过 100 款游戏，我们希望他们解释为什么拥有这么多游戏，例如他们可能经营游戏转售商店，或者只是喜欢收藏游戏。要有条件地添加此要求，可以使用 `Validator` 实例的 `sometimes` 方法。

```php
use Illuminate\Support\Fluent;

$validator->sometimes('reason', ['required', 'max:500'], function (Fluent $input) {
    return $input->games >= 100;
});
```

传给 `sometimes` 方法的第一个参数是要进行条件验证的字段名，第二个参数是要添加的规则列表。如果作为第三个参数传入的闭包返回 `true`，这些规则就会被添加。该方法使构建复杂条件验证变得轻松，甚至可以一次为多个字段添加条件验证：

```php
$validator->sometimes(['reason', 'cost'], 'required', function (Fluent $input) {
    return $input->games >= 100;
});
```

> [!NOTE]
> 传给闭包的 `$input` 参数是 `Illuminate\Support\Fluent` 的实例，可用于访问正在验证的输入数据和文件。

<a name="complex-conditional-array-validation"></a>
#### 复杂的条件数组验证

有时，你可能希望根据同一嵌套数组中另一个字段的值来验证某个字段，但并不知道该数组的索引。此时，可以让闭包接收第二个参数，它代表正在验证的数组中的当前单个元素：

```php
$input = [
    'channels' => [
        [
            'type' => 'email',
            'address' => 'abigail@example.com',
        ],
        [
            'type' => 'url',
            'address' => 'https://example.com',
        ],
    ],
];

$validator->sometimes('channels.*.address', 'email', function (Fluent $input, Fluent $item) {
    return $item->type === 'email';
});

$validator->sometimes('channels.*.address', 'url', function (Fluent $input, Fluent $item) {
    return $item->type !== 'email';
});
```

与传给闭包的 `$input` 参数一样，当属性数据为数组时，`$item` 参数是 `Illuminate\Support\Fluent` 的实例；否则，它是一个字符串。

<a name="validating-arrays"></a>
## 验证数组

如 [数组验证规则文档](#rule-array) 所述，`array` 规则接受一个允许的数组键列表。如果数组中包含任何其他键，验证就会失败：

```php
use Illuminate\Support\Facades\Validator;

$input = [
    'user' => [
        'name' => 'Taylor Otwell',
        'username' => 'taylorotwell',
        'admin' => true,
    ],
];

Validator::make($input, [
    'user' => ['array:name,username'],
]);
```

通常，你应始终指定数组中允许出现的键。否则，验证器的 `validate` 和 `validated` 方法会返回所有已验证数据，包括该数组及其所有键，即使其他嵌套数组验证规则并未验证这些键。

<a name="validating-nested-array-input"></a>
### 验证嵌套数组输入

验证嵌套数组形式的表单输入字段并不困难。可以使用「点表示法」验证数组中的属性。例如，如果传入的 HTTP 请求包含 `photos[profile]` 字段，可以这样验证：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($request->all(), [
    'photos.profile' => ['required', 'image'],
]);
```

你也可以验证数组中的每个元素。例如，要验证给定数组输入字段中的每个电子邮件地址都是唯一的，可以这样做：

```php
$validator = Validator::make($request->all(), [
    'users.*.email' => ['email', 'unique:users'],
    'users.*.first_name' => ['required_with:users.*.last_name'],
]);
```

同样，在 [语言文件中指定自定义验证消息](#custom-messages-for-specific-attributes) 时，可以使用 `*` 字符，轻松地为数组字段使用同一条验证消息：

```php
'custom' => [
    'users.*.email' => [
        'unique' => 'Each user must have a unique email address',
    ]
],
```

<a name="accessing-nested-array-data"></a>
#### 访问嵌套数组数据

有时，在为属性指定验证规则时，你可能需要访问某个嵌套数组元素的值。可以使用 `Rule::forEach` 方法实现。`forEach` 方法接受一个闭包，验证数组属性时每次迭代都会调用该闭包，并向其传入属性值及明确的、完全展开的属性名称。闭包应返回分配给该数组元素的规则数组：

```php
use App\Rules\HasPermission;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

$validator = Validator::make($request->all(), [
    'companies.*.id' => Rule::forEach(function (string|null $value, string $attribute) {
        return [
            Rule::exists(Company::class, 'id'),
            new HasPermission('manage-company', $value),
        ];
    }),
]);
```

<a name="error-message-indexes-and-positions"></a>
### 错误消息中的索引和位置

验证数组时，你可能希望在应用显示的错误消息中引用验证失败的特定元素的索引或位置。为此，可以在 [自定义验证消息](#manual-customizing-the-error-messages) 中使用 `:index`（从 `0` 开始）、`:position`（从 `1` 开始）或 `:ordinal-position`（从 `1st` 开始）占位符：

```php
use Illuminate\Support\Facades\Validator;

$input = [
    'photos' => [
        [
            'name' => 'BeachVacation.jpg',
            'description' => 'A photo of my beach vacation!',
        ],
        [
            'name' => 'GrandCanyon.jpg',
            'description' => '',
        ],
    ],
];

Validator::validate($input, [
    'photos.*.description' => ['required'],
], [
    'photos.*.description.required' => 'Please describe photo #:position.',
]);
```

在上面的示例中，验证会失败，用户将看到错误消息 _"Please describe photo #2."_。

如有需要，可以通过 `second-index`、`second-position`、`third-index`、`third-position` 等占位符引用更深层嵌套的索引和位置。

```php
'photos.*.attributes.*.string' => 'Invalid attribute for photo #:second-position.',
```

<a name="validating-files"></a>
## 验证文件

Laravel 提供多种可用于验证上传文件的规则，例如 `mimes`、`image`、`min` 和 `max`。虽然可以在验证文件时分别指定这些规则，但 Laravel 还提供了方便的流畅文件验证规则构建器：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rules\File;

Validator::validate($input, [
    'attachment' => [
        'required',
        File::types(['mp3', 'wav'])
            ->min(1024)
            ->max(12 * 1024),
    ],
]);
```

<a name="validating-files-file-types"></a>
#### 验证文件类型

虽然调用 `types` 方法时只需指定扩展名，但该方法实际上会读取文件内容并推断 MIME 类型，以验证文件的 MIME 类型。MIME 类型及其对应扩展名的完整列表可在以下位置找到：

[https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types](https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types)

<a name="validating-files-file-sizes"></a>
#### 验证文件大小

为方便起见，最小和最大文件大小可以指定为带有文件大小单位后缀的字符串，支持 `kb`、`mb`、`gb` 和 `tb` 后缀：

```php
File::types(['mp3', 'wav'])
    ->min('1kb')
    ->max('10mb');
```

<a name="validating-files-image-files"></a>
#### 验证图片文件

如果应用接受用户上传的图片，可以使用 `File` 规则的 `image` 构造方法，确保待验证文件是图片（jpg、jpeg、png、bmp、gif、webp、avif、heic 或 heif）。

此外，可以使用 `dimensions` 规则限制图片尺寸：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Rules\File;

Validator::validate($input, [
    'photo' => [
        'required',
        File::image()
            ->min(1024)
            ->max(12 * 1024)
            ->dimensions(Rule::dimensions()->maxWidth(1000)->maxHeight(500)),
    ],
]);
```

> [!NOTE]
> 有关验证图片尺寸的更多信息，请参阅 [尺寸规则文档](#rule-dimensions)。

> [!WARNING]
> 默认情况下，`image` 规则不允许 SVG 文件，因为它们可能带来 XSS 漏洞。如果需要允许 SVG 文件，可以向 `image` 规则传入 `allowSvg: true`：`File::image(allowSvg: true)`。

<a name="validating-files-image-dimensions"></a>
#### 验证图片尺寸

你也可以验证图片尺寸。例如，要验证上传图片的宽度至少为 1000 像素、高度至少为 500 像素，可以使用 `dimensions` 规则：

```php
use Illuminate\Validation\Rule;
use Illuminate\Validation\Rules\File;

File::image()->dimensions(
    Rule::dimensions()
        ->maxWidth(1000)
        ->maxHeight(500)
);
```

> [!NOTE]
> 有关验证图片尺寸的更多信息，请参阅 [尺寸规则文档](#rule-dimensions)。

<a name="validating-passwords"></a>
## 验证密码

为确保密码具有足够的复杂度，可以使用 Laravel 的 `Password` 规则对象：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rules\Password;

$validator = Validator::make($request->all(), [
    'password' => ['required', 'confirmed', Password::min(8)],
]);
```

`Password` 规则对象允许你轻松自定义应用的密码复杂度要求，例如要求密码至少包含一个字母、数字、符号或大小写混合的字符：

```php
// 至少需要 8 个字符……
Password::min(8);

// 最多允许 256 个字符……
Password::min(16)->max(256);

// 至少需要一个字母……
Password::min(8)->letters();

// 至少需要一个大写字母和一个小写字母……
Password::min(8)->mixedCase();

// 至少需要一个数字……
Password::min(8)->numbers();

// 至少需要一个符号……
Password::min(8)->symbols();
```

此外，可以使用 `uncompromised` 方法确保密码未在公开的密码泄露事件中泄露：

```php
Password::min(8)->uncompromised();
```

`Password` 规则对象内部使用 [k-匿名](https://en.wikipedia.org/wiki/K-anonymity) 模型，通过 [haveibeenpwned.com](https://haveibeenpwned.com) 服务判断密码是否泄露，同时不损害用户的隐私或安全。

默认情况下，如果密码在数据泄露中至少出现一次，就会被视为已泄露。可以通过 `uncompromised` 方法的第一个参数自定义此阈值：

```php
// 确保密码在同一次数据泄露中出现不超过 3 次……
Password::min(8)->uncompromised(3);
```

当然，你可以链式调用上述示例中的所有方法：

```php
Password::min(8)
    ->max(256)
    ->letters()
    ->mixedCase()
    ->numbers()
    ->symbols()
    ->uncompromised();
```

可以使用 `toPasswordRulesString` 方法将 `Password` 规则对象转换为适合 HTML `passwordrules` 属性的字符串：

```blade
<input
    type="password"
    name="password"
    autocomplete="new-password"
    passwordrules="{{ Password::defaults()->toPasswordRulesString() }}"
/>
```

<a name="defining-default-password-rules"></a>
#### 定义默认密码规则

在应用中的一个位置统一指定默认密码验证规则可能很方便。可以使用接受闭包的 `Password::defaults` 方法轻松实现。传给 `defaults` 方法的闭包应返回 Password 规则的默认配置。通常，应在应用的某个服务提供者的 `boot` 方法中调用 `defaults` 规则：

```php
use Illuminate\Validation\Rules\Password;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Password::defaults(function () {
        $rule = Password::min(8);

        return $this->app->isProduction()
            ? $rule->mixedCase()->uncompromised()
            : $rule;
    });
}
```

之后，要将默认规则应用于某个待验证密码时，可以不传参数调用 `defaults` 方法：

```php
'password' => ['required', Password::defaults()],
```

有时，你可能希望为默认密码验证规则附加其他验证规则。可以使用 `rules` 方法实现：

```php
use App\Rules\ZxcvbnRule;

Password::defaults(function () {
    $rule = Password::min(8)->rules([new ZxcvbnRule]);

    // ...
});
```

<a name="deriving-rules-from-json-schemas"></a>
## 从 JSON Schema 派生规则

如果应用使用 Laravel 的 [JSON Schema](/docs/{{version}}/ai-sdk#tool-input-schemas) 构建器或原始 JSON Schema 定义描述数据结构（例如 [Laravel MCP](/docs/{{version}}/mcp#tool-input-schemas) 中的工具输入），可以使用 `JsonSchema::rules` 方法自动从对象 schema 派生 Laravel 验证规则：

```php
use Illuminate\JsonSchema\JsonSchema;
use Illuminate\Support\Facades\Validator;

$schema = JsonSchema::object(fn ($s) => [
    'name' => $s->string()->max(50)->required(),
    'age' => $s->integer()->min(18),
    'role' => $s->string()->enum(['admin', 'user'])->required(),
]);

$validator = Validator::make($request->all(), JsonSchema::rules($schema));
```

`JsonSchema::rules` 方法也接受原始 JSON Schema 数组：

```php
use Illuminate\JsonSchema\JsonSchema;

$rules = JsonSchema::rules([
    'type' => 'object',
    'properties' => [
        'email' => ['type' => 'string', 'format' => 'email'],
    ],
    'required' => ['email'],
]);

// ['email' => ['required', 'string', 'email']]
```

可以在 Laravel 接受验证规则的任何位置使用派生出的规则，包括 [表单请求](#creating-form-requests) 的 `rules` 方法：

```php
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\JsonSchema\JsonSchema;

class StoreUserRequest extends FormRequest
{
    /**
     * 获取适用于请求的验证规则。
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return JsonSchema::rules(JsonSchema::object(fn ($s) => [
            'name' => $s->string()->max(50)->required(),
            'email' => $s->string()->email()->required(),
        ]));
    }
}
```

<a name="custom-validation-rules"></a>
## 自定义验证规则

<a name="using-rule-objects"></a>
### 使用规则对象

Laravel 提供了多种实用的验证规则，不过你也可能希望指定自己的规则。注册自定义验证规则的一种方式是使用规则对象。可以使用 `make:rule` Artisan 命令生成新的规则对象。下面使用此命令生成一个验证字符串是否为大写的规则。Laravel 会将新规则放在 `app/Rules` 目录中。如果该目录不存在，Laravel 会在你执行 Artisan 命令创建规则时创建它：

```shell
php artisan make:rule Uppercase
```

创建规则后，就可以定义其行为。规则对象包含一个 `validate` 方法，该方法接收属性名、属性值以及验证失败时应使用错误消息调用的回调：

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class Uppercase implements ValidationRule
{
    /**
     * 运行验证规则。
     */
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (strtoupper($value) !== $value) {
            $fail('The :attribute must be uppercase.');
        }
    }
}
```

定义规则后，可以将规则对象实例与其他验证规则一起传给验证器，从而附加该规则：

```php
use App\Rules\Uppercase;

$request->validate([
    'name' => ['required', 'string', new Uppercase],
]);
```

#### 翻译验证消息

除了向 `$fail` 闭包提供字面错误消息外，也可以提供 [翻译字符串键](/docs/{{version}}/localization)，并让 Laravel 翻译错误消息：

```php
if (strtoupper($value) !== $value) {
    $fail('validation.uppercase')->translate();
}
```

如有需要，可以将占位符替换值和首选语言分别作为第一个和第二个参数传给 `translate` 方法：

```php
$fail('validation.location')->translate([
    'value' => $this->value,
], 'fr');
```

#### 访问额外数据

如果自定义验证规则类需要访问正在验证的所有其他数据，规则类可以实现 `Illuminate\Contracts\Validation\DataAwareRule` 接口。该接口要求类定义 `setData` 方法。Laravel 会在验证开始前自动调用该方法，并传入所有待验证数据：

```php
<?php

namespace App\Rules;

use Illuminate\Contracts\Validation\DataAwareRule;
use Illuminate\Contracts\Validation\ValidationRule;

class Uppercase implements DataAwareRule, ValidationRule
{
    /**
     * 所有待验证数据。
     *
     * @var array<string, mixed>
     */
    protected $data = [];

    // ...

    /**
     * 设置待验证数据。
     *
     * @param  array<string, mixed>  $data
     */
    public function setData(array $data): static
    {
        $this->data = $data;

        return $this;
    }
}
```

或者，如果验证规则需要访问执行验证的验证器实例，可以实现 `ValidatorAwareRule` 接口：

```php
<?php

namespace App\Rules;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Contracts\Validation\ValidatorAwareRule;
use Illuminate\Validation\Validator;

class Uppercase implements ValidationRule, ValidatorAwareRule
{
    /**
     * 验证器实例。
     *
     * @var \Illuminate\Validation\Validator
     */
    protected $validator;

    // ...

    /**
     * 设置当前验证器。
     */
    public function setValidator(Validator $validator): static
    {
        $this->validator = $validator;

        return $this;
    }
}
```

<a name="using-closures"></a>
### 使用闭包

如果整个应用中只需要使用一次自定义规则，可以使用闭包代替规则对象。闭包接收属性名、属性值和验证失败时应调用的 `$fail` 回调：

```php
use Illuminate\Support\Facades\Validator;
use Closure;

$validator = Validator::make($request->all(), [
    'title' => [
        'required',
        'max:255',
        function (string $attribute, mixed $value, Closure $fail) {
            if ($value === 'foo') {
                $fail("The {$attribute} is invalid.");
            }
        },
    ],
]);
```

<a name="implicit-rules"></a>
### 隐式规则

默认情况下，如果待验证属性不存在或包含空字符串，则不会运行普通验证规则，包括自定义规则。例如，[unique](#rule-unique) 规则不会对空字符串运行：

```php
use Illuminate\Support\Facades\Validator;

$rules = ['name' => ['unique:users,name']];

$input = ['name' => ''];

Validator::make($input, $rules)->passes(); // true
```

要使自定义规则即使在属性为空时也能运行，该规则必须暗示该属性为必填项。要快速生成新的隐式规则对象，可以在 `make:rule` Artisan 命令中使用 `--implicit` 选项：

```shell
php artisan make:rule Uppercase --implicit
```

> [!WARNING]
> 「隐式」规则仅 _暗示_ 属性为必填项。缺失或为空的属性是否真的会导致验证失败，取决于你。
