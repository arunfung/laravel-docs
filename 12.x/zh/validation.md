
# 数据验证

- [简介](#introduction)
- [验证快速入门](#validation-quickstart)
    - [定义路由](#quick-defining-the-routes)
    - [创建控制器](#quick-creating-the-controller)
    - [编写验证逻辑](#quick-writing-the-validation-logic)
    - [显示验证错误](#quick-displaying-the-validation-errors)
    - [表单数据回填](#repopulating-forms)
    - [关于可选字段的说明](#a-note-on-optional-fields)
    - [验证错误响应格式](#validation-error-response-format)
- [表单请求验证](#form-request-validation)
    - [创建表单请求](#creating-form-requests)
    - [授权表单请求](#authorizing-form-requests)
    - [自定义错误消息](#customizing-the-error-messages)
    - [验证前数据预处理](#preparing-input-for-validation)
- [手动创建验证器](#manually-creating-validators)
    - [自动重定向](#automatic-redirection)
    - [命名错误包](#named-error-bags)
    - [自定义错误消息](#manual-customizing-the-error-messages)
    - [执行额外验证](#performing-additional-validation)
- [处理已验证数据](#working-with-validated-input)
- [处理错误消息](#working-with-error-messages)
    - [在语言文件中指定自定义消息](#specifying-custom-messages-in-language-files)
    - [在语言文件中指定属性名称](#specifying-attribute-in-language-files)
    - [在语言文件中指定值](#specifying-values-in-language-files)
- [可用验证规则](#available-validation-rules)
- [条件式添加规则](#conditionally-adding-rules)
- [验证数组](#validating-arrays)
    - [验证嵌套数组输入](#validating-nested-array-input)
    - [错误消息索引和位置](#error-message-indexes-and-positions)
- [验证文件](#validating-files)
- [验证密码](#validating-passwords)
- [自定义验证规则](#custom-validation-rules)
    - [使用规则对象](#using-rule-objects)
    - [使用闭包](#using-closures)
    - [隐式规则](#implicit-rules)

<a name="introduction"></a>
## 简介

Laravel 提供了多种不同的方法来验证应用程序的传入数据。最常见的是使用所有传入 HTTP 请求上都可用的 `validate` 方法。不过，我们也将讨论其他验证方法。

Laravel 包含了各种方便的验证规则，您可以将它们应用于数据，甚至提供了验证值在给定数据库表中是否唯一的能力。我们将详细介绍这些验证规则，以便您熟悉 Laravel 的所有验证功能。

<a name="validation-quickstart"></a>
## 快速开始

为了了解 Laravel 强大的验证功能，我们来看一个表单验证并将错误消息展示给用户的完整示例。通过阅读概述，这将会对你如何使用 Laravel 验证传入的请求数据有一个很好的理解：

<a name="quick-defining-the-routes"></a>
### 定义路由

首先，假设我们在 `routes/web.php` 路由文件中定义了下面这些路由：

```php
use App\Http\Controllers\PostController;

Route::get('/post/create', [PostController::class, 'create']);
Route::post('/post', [PostController::class, 'store']);
```

`GET` 路由会显示一个供用户创建新博客文章的表单，而 `POST` 路由会将新的博客文章存储到数据库中。

<a name="quick-creating-the-controller"></a>
### 创建控制器

接下来，让我们一起来看看处理这些路由的简单控制器。我们暂时留空了 `store` 方法：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class PostController extends Controller
{
    /**
     * 博客的表单视图
     */
    public function create(): View
    {
        return view('post.create');
    }

    /**
     * 存储博客的 Action
     */
    public function store(Request $request): RedirectResponse
    {
        // 验证并且执行存储逻辑

        $post = /** ... */

        return to_route('post.show', ['post' => $post->id]);
    }
}
```

<a name="quick-writing-the-validation-logic"></a>
### 编写验证逻辑

现在我们开始在 `store` 方法中编写用来验证新的博客文章的逻辑代码。为此，我们将使用 `Illuminate\Http\Request` 类提供的 `validate` 方法。如果验证通过，你的代码会继续正常运行。如果验证失败，则会抛出 `Illuminate\Validation\ValidationException` 异常，并自动将对应的错误响应返回给用户。


如果传统HTTP请求验证失败，将会生成重定向响应跳转至上个URL。若传入请求为XHR请求，则会返回[包含验证错误信息的JSON响应](#validation-error-response-format)。

为了更好地理解`validate`方法，让我们回到`store`方法：

```php
/**
 * 存储新博客文章
 */
public function store(Request $request): RedirectResponse
{
    $validated = $request->validate([
        'title' => 'required|unique:posts|max:255',
        'body' => 'required',
    ]);

    // 博客文章验证通过...

    return redirect('/posts');
}
```

如您所见，验证规则被传入`validate`方法。不必担心 - 所有可用验证规则都已[文档化](#available-validation-rules)。再次说明，如果验证失败，将会自动生成适当的响应。如果验证通过，控制器将继续正常执行。

或者，验证规则也可以指定为规则数组，而非单个`|`分隔的字符串：

```php
$validatedData = $request->validate([
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
]);
```

此外，您可以使用`validateWithBag`方法验证请求并将错误信息存储到[命名错误包](#named-error-bags)中：

```php
$validatedData = $request->validateWithBag('post', [
    'title' => ['required', 'unique:posts', 'max:255'],
    'body' => ['required'],
]);
```

<a name="stopping-on-first-validation-failure"></a>
#### 首次验证失败即停止

有时您可能希望在属性首次验证失败后停止执行后续验证规则。为此，可给属性分配`bail`规则：

```php
$request->validate([
    'title' => 'bail|required|unique:posts|max:255',
    'body' => 'required',
]);
```

在此示例中，如果`title`属性的`unique`规则失败，将不会检查`max`规则。规则将按照分配的顺序进行验证。

<a name="a-note-on-nested-attributes"></a>
#### 关于嵌套属性的说明

如果传入的 HTTP 请求包含 「嵌套」 字段数据，您可以在验证规则中使用 「点」 语法来指定这些字段：

```php
$request->validate([
    'title' => 'required|unique:posts|max:255',
    'author.name' => 'required',
    'author.description' => 'required',
]);
```

另一方面，如果您的字段名包含文字句点，可以通过在句点前添加反斜杠来显式阻止其被解释为 「点」 语法：

```php
$request->validate([
    'title' => 'required|unique:posts|max:255',
    'v1\.0' => 'required',
]);
```

<a name="quick-displaying-the-validation-errors"></a>
### 显示验证错误

那么，如果传入请求字段未通过给定的验证规则会怎样呢？ 如前所述，Laravel 会自动将用户重定向到之前的位置。 此外，所有验证错误和 [请求输入](https://laravel.com/docs/laravel/12.x/requests#retrieving-old-input) 都会自动 [闪存到 Session](https://laravel.com/docs/laravel/12.x/session#flash-data) 。

`Illuminate\View\Middleware\ShareErrorsFromSession` 中间件（由 `web` 中间件组提供）会将 `$errors` 变量共享给您应用的所有视图。 应用此中间件后， `$errors` 变量将始终在视图中可用，您可以放心地假设该变量已定义并可安全使用。 `$errors` 变量是 `Illuminate\Support\MessageBag` 的一个实例。 有关此对象的更多信息，请 [查阅其文档](#working-with-error-messages) 。

在我们的示例中，当验证失败时，用户将被重定向到控制器的 `create` 方法，使我们能够在视图中显示错误信息：

```blade
<!-- /resources/views/post/create.blade.php -->

<h1>创建文章</h1>

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

Laravel 的内置验证规则每个都有对应的错误消息，这些消息位于您应用的 `lang/en/validation.php` 文件中。 如果您的应用没有 `lang` 目录，您可以使用 `lang:publish` Artisan 命令让 Laravel 创建它。

在 `lang/en/validation.php` 文件中，您会找到每个验证规则的翻译条目。 您可以根据应用的需求自由更改或修改这些消息。

此外，您可以将此文件复制到其他语言目录，以翻译成您应用所需的语言。 要了解更多关于 Laravel 本地化的信息，请查阅完整的 [本地化文档](https://laravel.com/docs/laravel/12.x/localization) 。

> [!警告]
> 默认情况下，Laravel 应用骨架不包含 `lang` 目录。 如果您想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令来发布它们。

<a name="quick-xhr-requests-and-validation"></a>
#### XHR 请求与验证

在这个例子中，我们使用了传统表单向应用发送数据。 然而，许多应用会收到来自 JavaScript 驱动前端的 XHR 请求。 当在 XHR 请求中使用 `validate` 方法时，Laravel 不会生成重定向响应。 相反，Laravel 会生成一个 [包含所有验证错误的 JSON 响应](#validation-error-response-format) 。 此 JSON 响应将附带 422 HTTP 状态码一起发送。

<a name="the-at-error-directive"></a>
#### `@error` 指令

您可以使用 `@error` [Blade](https://laravel.com/docs/laravel/12.x/blade) 指令来快速判断给定属性是否存在验证错误消息。 在 `@error` 指令内部，您可以回显 `$message` 变量来显示错误消息：

```blade
<!-- /resources/views/post/create.blade.php -->

<label for="title">文章标题</label>

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

如果您使用的是 [命名错误包](#named-error-bags) ，可以将错误包的名称作为第二个参数传递给 `@error` 指令：

```blade
<input ... class="@error('title', 'post') is-invalid @enderror">
```

<a name="repopulating-forms"></a>
### 表单数据回填

当 Laravel 因验证错误而生成重定向响应时，框架会自动 [将请求的所有输入数据闪存到 Session](https://laravel.com/docs/laravel/12.x/session#flash-data) 。 这样做的目的是让您可以在下次请求时方便地访问这些输入数据，并重新填充用户尝试提交的表单。

要从上一个请求中获取闪存的输入数据，可以在 `Illuminate\Http\Request` 实例上调用 `old` 方法。 `old` 方法会从 [Session](https://laravel.com/docs/laravel/12.x/session) 中提取之前闪存的输入数据：

```php
$title = $request->old('title');
```

Laravel 还提供了一个全局的 `old` 辅助函数。 如果您在 [Blade 模板](https://laravel.com/docs/laravel/12.x/blade) 中显示旧输入数据，使用 `old` 辅助函数来回填表单会更加方便。 如果给定字段没有旧的输入数据，将返回 `null`：

```blade
<input type="text" name="title" value="{{ old('title') }}">
```

<a name="a-note-on-optional-fields"></a>
### 关于可选字段的说明

默认情况下，Laravel 在应用的全局中间件堆栈中包含 `TrimStrings` 和 `ConvertEmptyStringsToNull` 中间件。 因此，如果您不希望验证器将 `null` 值视为无效，通常需要将「可选」请求字段标记为 `nullable` 。 例如：

```php
$request->validate([
    'title' => 'required|unique:posts|max:255',
    'body' => 'required',
    'publish_at' => 'nullable|date',
]);
```

在这个例子中，我们指定 `publish_at` 字段可以为 `null` 或有效的日期表示。如果没有将 `nullable` 修饰符添加到规则定义中，则验证器会将 `null` 视为无效日期。

<a name="validation-error-response-format"></a>
### 验证错误响应格式

当您的应用程序抛出 `Illuminate\Validation\ValidationException` 异常，并且传入的 HTTP 请求希望返回 JSON 响应时，Laravel 将自动为您格式化错误消息，并返回 `422 Unprocessable Entity` HTTP 响应。

下面是验证错误的 JSON 响应格式示例。注意，嵌套的错误键会被转换为「点」符号格式：

```json
{
    "message": "The team name must be a string. (and 4 more errors)",
    "errors": {
        "team_name": [
            "The team name must be a string.",
            "The team name must be at least 1 characters."
        ],
        "authorization.role": [
            "The selected authorization.role is invalid."
        ],
        "users.0.email": [
            "The users.0.email field is required."
        ],
        "users.2.email": [
            "The users.2.email must be a valid email address."
        ]
    }
}
```

<a name="form-request-validation"></a>
## 表单请求验证

<a name="creating-form-requests"></a>
### 创建表单请求

对于更复杂的验证场景，您可能希望创建一个「表单请求」。表单请求是自定义请求类，封装了自己的验证和授权逻辑。要创建一个表单请求类，您可以使用 `make:request` Artisan CLI 命令：

```shell
php artisan make:request StorePostRequest
```

生成的表单请求类将被放置在 `app/Http/Requests` 目录中。如果此目录不存在，则在运行 `make:request` 命令时将创建该目录。Laravel 生成的每个表单请求都有两个方法：`authorize` 和 `rules`。



正如您可能想到的，`authorize` 方法负责确定当前已认证的用户是否可以执行请求所代表的操作，而 `rules` 方法则返回应当应用于请求数据的验证规则：

```php
/**
 * 获取应用于请求的验证规则。
 *
 * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
 */
public function rules(): array
{
    return [
        'title' => 'required|unique:posts|max:255',
        'body' => 'required',
    ];
}
```

> **注意**
> 您可以在 `rules` 方法的签名中类型提示任何您需要的依赖项。它们将通过 Laravel [服务容器](/docs/laravel/12.x/container "服务容器") 自动解析。

那么，验证规则是如何被评估的呢？您只需要在控制器方法中对请求进行类型提示。传入的表单请求会在控制器方法被调用之前进行验证，这意味着您不需要在控制器中添加任何验证逻辑：

```php
/**
 * 存储新的博客文章。
 */
public function store(StorePostRequest $request): RedirectResponse
{
    // 传入的请求是有效的...

    // 检索已验证的输入数据...
    $validated = $request->validated();

    // 检索部分验证过的输入数据...
    $validated = $request->safe()->only(['name', 'email']);
    $validated = $request->safe()->except(['name', 'email']);

    // 存储博客文章...

    return redirect('/posts');
}
```

如果验证失败，将生成一个重定向响应，将用户送回他们之前的位置。错误信息也会被闪存到 session 中，以便显示。如果请求是 XHR 请求，将向用户返回一个 HTTP 422 状态码的响应，其中包含 [验证错误的 JSON 表示](#validation-error-response-format "验证错误的 JSON 表示")。

> **注意**
> 需要为您的 Inertia 驱动的 Laravel 前端添加实时表单请求验证吗？ 请查看 [Laravel 实时服务器端表单验证扩展](/docs/laravel/12.x/precognition)。



<a name="performing-additional-validation-on-form-requests"></a>
#### 执行附加验证

有时，在完成初始验证后，你需要执行额外的验证。您可以使用表单请求的 `after` 方法来完成此操作。

`after` 方法应返回一个可调用或闭包数组，这些数组将在验证完成后调用。给定的可调用程序将接收一个 `Illuminate\Validation\Validator` 实例，允许你在必要时引发额外的错误消息：

```php
use Illuminate\Validation\Validator;

/**
 * 获取请求的「after」验证可调用项。
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

如上所述，`after` 方法返回的数组也可能包含可调用的类。这些类的 `__invoke` 方法将接收一个 `Illuminate\Validation\Validator` 实例：

```php
use App\Validation\ValidateShippingTime;
use App\Validation\ValidateUserStatus;
use Illuminate\Validation\Validator;

/**
 * 获取请求的「after」验证可调用项。
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
#### 在首次验证失败时停止

通过添加 `stopOnFirstFailure` 属性到请求类，你可以通知验证器，一旦发生单个验证失败，它就应该停止验证所有属性：

```php
/**
 * 指示验证程序是否应在第一个规则失败时停止。
 *
 * @var bool
 */
protected $stopOnFirstFailure = true;
```

<a name="customizing-the-redirect-location"></a>
#### 自定义重定向位置

当表单请求验证失败时，生成的重定向响应，将会使用户返回到原来的位置。不过，你可以自由地自定义此行为。如果要这么做，请在表单请求中定义 `$redirect` 属性：

```php
/**
 * 验证失败时，用户应当跳转的URI
 *
 * @var string
 */
protected $redirect = '/dashboard';
```



或者，如果您想将用户重定向到命名路由，您可以定义一个 `$redirectRoute ` 属性：

```php
/**
 * 如果验证失败，用户应该被重定向到的路由。
 *
 * @var string
 */
protected $redirectRoute = 'dashboard';
```

<a name="authorizing-form-requests"></a>
### 授权表单请求

表单请求类还包含一个 `authorize` 方法。在这个方法中，您可以确定已认证的用户是否真正有权更新给定的资源。例如，您可以确定用户是否真的拥有他们试图更新的博客评论。通常，您会在这个方法中与您的 [授权门禁和策略](/docs/laravel/12.x/authorization) 进行交互:

```php
use App\Models\Comment;

/**
 * 确定用户是否有权进行此请求。
 */
public function authorize(): bool
{
    $comment = Comment::find($this->route('comment'));

    return $comment && $this->user()->can('update', $comment);
}
```

由于所有表单请求都继承自 Laravel 的基础请求类，我们可以使用 `user` 方法来访问当前已认证的用户。另外，注意上面示例中对 `route` 方法的调用。这个方法允许您访问在被调用路由上定义的 URI 参数，比如下面示例中的 `{comment}` 参数：

```php
Route::post('/comment/{comment}');
```

因此，如果您的应用程序利用了 [路由模型绑定](/docs/laravel/12.x/routing#route-model-binding)，您的代码可以通过将解析后的模型作为请求的属性来访问，从而变得更加简洁：

```php
return $this->user()->can('update', $this->comment);
```

如果 `authorize` 方法返回 `false`，一个带有 403 状态码的 HTTP 响应将会被自动返回，并且您的控制器方法将不会被执行。



如果您计划在应用程序的其他部分处理请求的授权逻辑，您可以完全移除 `authorize` 方法，或者简单地返回 `true` ：

```php
/**
 * 确定用户是否有权处理此请求。
 */
public function authorize(): bool
{
    return true;
}
```

> **注意**
> 你可以在 `authorize` 方法的签名中键入提示你需要的任何依赖项。 它将会使用 Laravel  [服务容器](/docs/laravel/12.x/container) 自动解析。

<a name="customizing-the-error-messages"></a>
### 自定义错误消息

您可以通过重写 `messages` 方法来自定义表单请求使用的错误消息。此方法应返回一个属性 / 规则对及其对应错误消息的数组：

```php
/**
 * 获取定义的验证规则的错误消息。
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

Laravel 的许多内置验证规则错误消息包含 `:attribute` 占位符。如果您想要将验证消息中的 `:attribute` 占位符替换为自定义属性名，可以通过重写 `attributes` 方法来指定自定义名称。此方法应返回一个属性 / 名称对的数组：

```php
/**
 * 获取验证器错误的自定义属性。
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
### 准备验证输入

如果您需要在应用验证规则之前准备或清理请求中的任何数据，可以使用 `prepareForValidation` 方法：

```php
use Illuminate\Support\Str;

/**
 * 准备验证数据。
 */
protected function prepareForValidation(): void
{
    $this->merge([
        'slug' => Str::slug($this->slug),
    ]);
}
```



同样，如果您需要在验证完成后规范化任何请求数据，可以使用 `passedValidation` 方法：

```php
/**
 * 处理验证通过的请求。
 */
protected function passedValidation(): void
{
    $this->replace(['name' => 'Taylor']);
}
```

<a name="manually-creating-validators"></a>
## 手动创建验证器

如果您不想在请求上使用 `validate` 方法，您可以使用 `Validator` [门面](/docs/laravel/12.x/facades) 手动创建一个验证器实例。门面上的 `make` 方法生成一个新的验证器实例:

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class PostController extends Controller
{
    /**
     * 存储一篇新的博客文章。
     */
    public function store(Request $request): RedirectResponse
    {
        $validator = Validator::make($request->all(), [
            'title' => 'required|unique:posts|max:255',
            'body' => 'required',
        ]);

        if ($validator->fails()) {
            return redirect('/post/create')
                ->withErrors($validator)
                ->withInput();
        }

        // 检索验证后的输入...
        $validated = $validator->validated();

        // 检索验证后输入的一部分...
        $validated = $validator->safe()->only(['name', 'email']);
        $validated = $validator->safe()->except(['name', 'email']);

        // 存储博客文章...

        return redirect('/posts');
    }
}
```

传递给 `make` 方法的第一个参数是要验证的数据。第二个参数是应用于数据的验证规则数组。

在确定请求验证是否失败后，您可以使用 `withErrors` 方法将错误消息闪存到会话中。当使用此方法时， `$errors` 变量将在重定向后自动与您的视图共享，允许您轻松地将它们显示给用户。 `withErrors` 方法接受一个验证器、一个 `MessageBag` 或一个 PHP `array`。



#### 首次验证失败时停止

`stopOnFirstFailure` 方法将通知验证器，一旦发生单个验证失败，它就会停止验证所有属性：

```php
if ($validator->stopOnFirstFailure()->fails()) {
    // ...
}
```

<a name="automatic-redirection"></a>
### 自动重定向

如果您想手动创建一个验证程序实例，但仍然利用 HTTP 请求的 `validate` 方法提供的自动重定向，则可以在现有的验证程序实例上调用 `validate` 方法。如果验证失败，用户将自动重定向，或者在 XHR 请求的情况下，将 [返回JSON响应](#validation-error-response-format):

```php
Validator::make($request->all(), [
    'title' => 'required|unique:posts|max:255',
    'body' => 'required',
])->validate();
```

如果验证失败，你可以使用 `validateWithBag` 方法将错误消息存储在 [命名错误包](#named-error-bags) 中：

```php
Validator::make($request->all(), [
    'title' => 'required|unique:posts|max:255',
    'body' => 'required',
])->validateWithBag('post');
```

<a name="named-error-bags"></a>
### 命名错误包

如果您在一个单页面上有多个表单，您可能希望命名包含验证错误的 `MessageBag` ，以便检索特定表单的错误消息。要实现这一点，请将名称作为第二个参数传递给 `withErrors` ：

```php
return redirect('/register')->withErrors($validator, 'login');
```

您可以在之后从 `$errors` 变量访问命名的 `MessageBag` 实例：

```blade
{{ $errors->login->first('email') }}
```

<a name="manual-customizing-the-error-messages"></a>
### 自定义错误消息

如果需要，您可以提供验证器实例应该使用的自定义错误消息，替换 Laravel 提供的默认错误消息。有几种方法可以指定自定义消息。首先，您可以将自定义消息作为第三个参数传递给 `Validator::make` 方法：

```php
$validator = Validator::make($input, $rules, $messages = [
    'required' => 'The :attribute field is required.',
]);
```



在本例中，`:attribute` 占位符将替换为正在验证字段的实际名称。您也可以在验证消息中使用其他占位符。例如

```php
$messages = [
    'same' => 'The :attribute and :other must match.',
    'size' => 'The :attribute must be exactly :size.',
    'between' => 'The :attribute value :input is not between :min - :max.',
    'in' => 'The :attribute must be one of the following types: :values',
];
```

<a name="specifying-a-custom-message-for-a-given-attribute"></a>
#### 给自定义消息指定属性

有时，你可能希望仅为特定属性指定自定义错误消息。您可以使用点 「.」表示法。首先指定属性的名称，然后指定规则：

```php
$messages = [
    'email.required' => 'We need to know your email address!',
];
```

<a name="specifying-custom-attribute-values"></a>
#### 指定自定义属性值

Laravel 的许多内置错误消息都包括一个 `:attribute` 占位符，该占位符被替换为正在验证的字段或属性的名称。要自定义用于替换特定字段的占位符的值，可以将自定义属性数组作为第四个参数传递给 `Validator::make` 方法：

```php
$validator = Validator::make($input, $rules, $messages, [
    'email' => 'email address',
]);
```

<a name="performing-additional-validation"></a>
### 执行附加验证

有时，在初始验证完成后，您需要执行额外的验证。您可以使用验证器的 `after` 方法来实现这一点。 `after` 方法接受一个闭包或一个可调用数组，这些闭包或数组将在验证完成后调用。给定的可调用程序将接收一个 `Illuminate\Validation\Validator` 实例，允许你在必要时引发额外的错误消息：

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



如上所述， `after` 方法也接受一个可调用的对象数组，如果你的 「after validation」逻辑被封装在可调用类中，这将特别方便，这些类将通过其 `__invoke` 方法接收一个  `Illuminate\Validation\Validator` 实例：

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
## 使用已验证过的输入

在使用表单请求或手动创建的验证器实例验证传入的请求数据之后，您可能希望检索实际经过验证的传入请求数据。这可以通过几种方式实现。首先，你可以在表单请求或验证器实例上调用 `validated` 方法。这个方法返回一个经过验证的数据数组：

```php
$validated = $request->validated();

$validated = $validator->validated();
```

或者，你可以在表单请求或验证器实例上调用 `safe` 方法。这个方法返回一个  `Illuminate\Support\ValidatedInput` 实例。这个对象暴露了  `only` ， `except` 和 `all` 方法来检索已验证数据的子集或整个已验证数据的数组：

```php
$validated = $request->safe()->only(['name', 'email']);

$validated = $request->safe()->except(['name', 'email']);

$validated = $request->safe()->all();
```

此外， `Illuminate\Support\ValidatedInput` 实例可以像数组一样被迭代和访问：

```php
// 验证过的数据可以被迭代...
foreach ($request->safe() as $key => $value) {
    // ...
}

// 验证过的数据可以作为数组访问...
$validated = $request->safe();

$email = $validated['email'];
```

如果您想添加额外的字段到已验证的数据，可以调用 `merge` 方法：

```php
$validated = $request->safe()->merge(['name' => 'Taylor Otwell']);
```



如果您想将已验证的数据作为 [集合](/docs/laravel/12.x/collections) 实例检索, 您可以调用 `collect` 方法：

```php
$collection = $request->safe()->collect();
```

<a name="working-with-error-messages"></a>
## 处理错误消息

在 `Validator` 实例上调用 `errors` 方法后，您将收到一个 `Illuminate\Support\MessageBag` 实例，它有多种方便的方法来处理错误消息。自动提供给所有视图的 `$errors` 变量也是 `MessageBag` 类的实例。

<a name="retrieving-the-first-error-message-for-a-field"></a>
#### 检索字段的第一个错误消息

要检索给定字段的第一个错误消息，请使用 `first` 方法：

```php
$errors = $validator->errors();

echo $errors->first('email');
```

<a name="retrieving-all-error-messages-for-a-field"></a>
#### 检索字段的所有错误消息

如果您需要检索给定字段的所有消息数组，请使用 `get` 方法：

```php
foreach ($errors->get('email') as $message) {
    // ...
}
```

如果您正在验证数组表单字段，可以使用 `*` 字符检索数组中每个元素的所有消息：

```php
foreach ($errors->get('attachments.*') as $message) {
    // ...
}
```

<a name="retrieving-all-error-messages-for-all-fields"></a>
#### 检索所有字段的所有错误消息

要检索所有字段的所有消息数组，请使用 `all` 方法：

```php
foreach ($errors->all() as $message) {
    // ...
}
```

<a name="determining-if-messages-exist-for-a-field"></a>
#### 确定字段是否存在消息

`has` 方法可用于确定给定字段是否存在任何错误消息：

```php
if ($errors->has('email')) {
    // ...
}
```



<a name="specifying-custom-messages-in-language-files"></a>
### 在语言文件中指定自定义消息

Laravel 的内置验证规则都有一个错误消息，位于应用程序的 `lang/en/validation.php` 文件中。如果您的应用没有 `lang` 目录，您可以让 Laravel 使用 `lang:publish`  Artisan 命令创建它。

在 `lang/en/validation.php` 文件中，您将找到每个验证规则的翻译条目。您可以根据应用程序的需要自由地更改或修改这些消息。

此外，您可以将此文件复制到另一个语言目录，以便为您应用程序的语言翻译消息。要了解更多有关 Laravel 本地化的信息，请查看完整的 [本地化文档](/docs/laravel/12.x/localization)。

> **警告**
> 默认，Laravel 应用程序骨架不包含 `lang` 目录。如果您想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

<a name="custom-messages-for-specific-attributes"></a>
#### 为特定属性自定义消息

您可以在应用程序的验证语言文件中自定义用于指定属性和规则组合的错误消息。为此，您可以添加消息自定义到您应用程序 `lang/xx/validate.php` 语言文件的 `custom` 数组中：

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

Laravel的许多内置错误信息都包含一个 `:attribute` 占位符，它被正在验证的字段或属性的名称所替换。如果您想用一个自定义值替换验证消息的 `:attribute` 部分，你可以在您的 ` lang/xx/validate.php` 语言文件的 `attributes` 数组中指定自定义属性名称：

```php
'attributes' => [
    'email' => 'email address',
],
```

> **警告**
> 默认，Laravel 应用程序骨架不包含 `lang` 目录。如果您想自定义 Laravel 的语言文件，您可以通过 `lang:publish` Artisan命令发布它们。



<a name="specifying-values-in-language-files"></a>
### 在语言文件中指定值

Laravel 的一些内置验证规则错误消息包含一个 `:value` 占位符，它会被替换为请求属性的当前值。但是，有时您可能需要将验证消息的 `:value` 部分替换为值的自定义表示。例如，考虑以下规则，该规则指定当 `payment_type` 的值为 `cc` 时，需要提供信用卡号码：

```php
Validator::make($request->all(), [
    'credit_card_number' => 'required_if:payment_type,cc'
]);
```

如果此验证规则失败，它将产生以下错误消息：

```text
The credit card number field is required when payment type is cc.
```

您可以在 `lang/xx/validation.php` 语言文件中定义一个 `values` 数组，以指定一个更加友好的值表示，而不是展示 `cc` 作为支付类型值：
```php
'values' => [
    'payment_type' => [
        'cc' => 'credit card'
    ],
],
```

> **警告**
> 默认情况下，Laravel 应用程序骨架不包含 `lang` 目录。如果您想自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布它们。

定义这个值后，验证规则将产生以下错误消息：

```text
The credit card number field is required when payment type is credit card.
```

<a name="available-validation-rules"></a>
## 可用的验证规则

以下是所有可用验证规则及其功能的列表：

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



#### 布尔型

<div class="collection-method-list" markdown="1">

[Accepted](#rule-accepted)
[Accepted If](#rule-accepted-if)
[Boolean](#rule-boolean)
[Declined](#rule-declined)
[Declined If](#rule-declined-if)

</div>

#### 字符串型

<div class="collection-method-list" markdown="1">

[Active URL](#rule-active-url)
[Alpha](#rule-alpha)
[Alpha Dash](#rule-alpha-dash)
[Alpha Numeric](#rule-alpha-num)
[Ascii](#rule-ascii)
[Confirmed](#rule-confirmed)
[Current Password](#rule-current-password)
[Different](#rule-different)
[Doesnt Start With](#rule-doesnt-start-with)
[Doesnt End With](#rule-doesnt-end-with)
[Email](#rule-email)
[Ends With](#rule-ends-with)
[Enum](#rule-enum)
[Hex Color](#rule-hex-color)
[In](#rule-in)
[IP Address](#rule-ip)
[JSON](#rule-json)
[Lowercase](#rule-lowercase)
[MAC Address](#rule-mac)
[Max](#rule-max)
[Min](#rule-min)
[Not In](#rule-not-in)
[Regular Expression](#rule-regex)
[Not Regular Expression](#rule-not-regex)
[Same](#rule-same)
[Size](#rule-size)
[Starts With](#rule-starts-with)
[String](#rule-string)
[Uppercase](#rule-uppercase)
[URL](#rule-url)
[ULID](#rule-ulid)
[UUID](#rule-uuid)

</div>

#### 数字型

<div class="collection-method-list" markdown="1">

[Between](#rule-between)
[Decimal](#rule-decimal)
[Different](#rule-different)
[Digits](#rule-digits)
[Digits Between](#rule-digits-between)
[Greater Than](#rule-gt)
[Greater Than Or Equal](#rule-gte)
[Integer](#rule-integer)
[Less Than](#rule-lt)
[Less Than Or Equal](#rule-lte)
[Max](#rule-max)
[Max Digits](#rule-max-digits)
[Min](#rule-min)
[Min Digits](#rule-min-digits)
[Multiple Of](#rule-multiple-of)
[Numeric](#rule-numeric)
[Same](#rule-same)
[Size](#rule-size)

</div>

#### 数组型

<div class="collection-method-list" markdown="1">

[Array](#rule-array)
[Between](#rule-between)
[Contains](#rule-contains)
[Distinct](#rule-distinct)
[In Array](#rule-in-array)
[In Array Keys](#rule-in-array-keys)
[List](#rule-list)
[Max](#rule-max)
[Min](#rule-min)
[Size](#rule-size)

</div>

#### 日期型

<div class="collection-method-list" markdown="1">

[After](#rule-after)
[After Or Equal](#rule-after-or-equal)
[Before](#rule-before)
[Before Or Equal](#rule-before-or-equal)
[Date](#rule-date)
[Date Equals](#rule-date-equals)
[Date Format](#rule-date-format)
[Different](#rule-different)
[Timezone](#rule-timezone)

</div>

#### 文件型

<div class="collection-method-list" markdown="1">

[Between](#rule-between)
[Dimensions](#rule-dimensions)
[Extensions](#rule-extensions)
[File](#rule-file)
[Image](#rule-image)
[Max](#rule-max)
[MIME Types](#rule-mimetypes)
[MIME Type By File Extension](#rule-mimes)
[Size](#rule-size)

</div>

#### 数据库型

<div class="collection-method-list" markdown="1">

[Exists](#rule-exists)
[Unique](#rule-unique)

</div>



#### 实用工具

<div class="collection-method-list" markdown="1">

[Any Of](#rule-anyof)
[Bail](#rule-bail)
[Exclude](#rule-exclude)
[Exclude If](#rule-exclude-if)
[Exclude Unless](#rule-exclude-unless)
[Exclude With](#rule-exclude-with)
[Exclude Without](#rule-exclude-without)
[Filled](#rule-filled)
[Missing](#rule-missing)
[Missing If](#rule-missing-if)
[Missing Unless](#rule-missing-unless)
[Missing With](#rule-missing-with)
[Missing With All](#rule-missing-with-all)
[Nullable](#rule-nullable)
[Present](#rule-present)
[Present If](#rule-present-if)
[Present Unless](#rule-present-unless)
[Present With](#rule-present-with)
[Present With All](#rule-present-with-all)
[Prohibited](#rule-prohibited)
[Prohibited If](#rule-prohibited-if)
[Prohibited If Accepted](#rule-prohibited-if-accepted)
[Prohibited If Declined](#rule-prohibited-if-declined)
[Prohibited Unless](#rule-prohibited-unless)
[Prohibits](#rule-prohibits)
[Required](#rule-required)
[Required If](#rule-required-if)
[Required If Accepted](#rule-required-if-accepted)
[Required If Declined](#rule-required-if-declined)
[Required Unless](#rule-required-unless)
[Required With](#rule-required-with)
[Required With All](#rule-required-with-all)
[Required Without](#rule-required-without)
[Required Without All](#rule-required-without-all)
[Required Array Keys](#rule-required-array-keys)
[Sometimes](#validating-when-present)

</div>

<a name="rule-accepted"></a>
#### accepted

待验证的字段必须是 `「yes」` ， `「on」` ， `1` ，`「1」` ， `true` ，或 `「true」` 。这对于验证 「服务条款」 接受情况或相似字段很有用。

<a name="rule-accepted-if"></a>
#### accepted_if:anotherfield,value,...

如果正在验证的另一个字段等于指定值，则正在验证的字段必须为 `「yes」` ， `「on」` ，  `1` ， `「1」` ， `true` ，或 `「true」` 。这对于验证 「服务条款」 接受情况或类似字段很有用。

<a name="rule-active-url"></a>
#### active_url

根据 PHP 函数 `dns_get_record` ，验证中的字段必须具有有效的 A 或 AAAA 记录。提供的 URL 的主机名在传递给 `dns_get_record` 之前使用 PHP 函数 `parse_url` 提取。

<a name="rule-after"></a>
#### after:_date_

验证中的字段必须是给定日期之后的值。该日期将被传递到 PHP 函数 `strtotime` 中，以便转换为有效的 `DateTime` 实例：

```php
'start_date' => 'required|date|after:tomorrow'
```



您可以指定另一个字段与日期进行比较，而不是传递要由 `strtotime` 计算的日期字符串：

```php
'finish_date' => 'required|date|after:start_date'
```

为方便起见，基于日期的规则可以使用流畅的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->after(today()->addDays(7)),
],
```

`afterToday` 和 `todayOrAfter` 方法可以分别用来流利地表示日期必须在今天之后或今天或之后：

```php
'start_date' => [
    'required',
    Rule::date()->afterToday(),
],
```

<a name="rule-after-or-equal"></a>
#### after\_or\_equal:_date_

待验证的字段必须是在给定日期之后或等于给定日期的值。更多信息，请查看 [after](#rule-after) 规则。

为方便起见，基于日期的规则可以使用流畅的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->afterOrEqual(today()->addDays(7)),
],
```

<a name="rule-anyof"></a>
#### anyOf

`Rule::anyOf` 验证规则允许您指定验证的字段必须满足任何给定的验证规则集。例如，下面的规则将验证 `username` 字段是一个电子邮件地址还是一个至少6个字符长的字母数字字符串（包括破折号）：

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
待验证的字段必须完全是包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=) 和 [\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=)中的 Unicode 字母字符。



要将此验证规则限制为 ASCII 范围内的字符（ ` a-z ` 和 `A-Z` ），您可以为验证规则提供  `ASCII` 选项：

```php
'username' => 'alpha:ascii',
```

<a name="rule-alpha-dash"></a>
#### alpha_dash

验证的字段必须完全是包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=) , [\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=) , [\p{N}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AN%3A%5D&g=&i=) 中的 Unicode 字母数字字符，以及 ASCII 破折号 ( `-` ) 和 ASCII 下划线 ( `_` )。

要将此验证规则限制为 ASCII 范围内的字符（ ` a-z ` 和 `A-Z` ，和 `0-9` ），您可以为验证规则提供 `ASCII` 选项：

```php
'username' => 'alpha_dash:ascii',
```

<a name="rule-alpha-num"></a>
#### alpha_num

待验证的字段必须完全是包含在 [\p{L}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AL%3A%5D&g=&i=), [\p{M}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AM%3A%5D&g=&i=), 和 [\p{N}](https://util.unicode.org/UnicodeJsps/list-unicodeset.jsp?a=%5B%3AN%3A%5D&g=&i=)中的 Unicode 字母字符。

要将此验证规则限制为 ASCII 范围内的字符（ ` a-z ` 和 `A-Z` ，和 `0-9` ），您可以为验证规则提供 `ASCII` 选项：

```php
'username' => 'alpha_num:ascii',
```

<a name="rule-array"></a>
#### array

待验证字段必须是一个 PHP 数组。

当向 `array` 规则提供附加值时，输入数组中的每个键都必须出现在提供给规则的值列表中。在以下示例中，输入数组中的 `admin` 键无效，因为它不包含在提供给 `array` 规则的值列表中：

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
    'user' => 'array:name,username',
]);
```



通常，您应该始终指定允许出现在数组中的数组键。

<a name="rule-ascii"></a>
#### ascii

待验证的字段必须完全是 7 位的 ASCII 字符。

<a name="rule-bail"></a>
#### bail

字段首次验证失败后停止运行验证规则。

虽然 `bail` 规则只会在遇到验证失败时停止验证特定字段，但 `stopOnFirstFailure` 方法会通知验证器，一旦发生单个验证失败，它应该停止验证所有属性：

```php
if ($validator->stopOnFirstFailure()->fails()) {
    // ...
}
```

<a name="rule-before"></a>
#### before:_date_

待验证字段的值对应的日期必须在给定的日期之前。这个日期将被传递给 PHP 函数 `strtotime` 以便转化为有效的 `DateTime` 实例。此外，像 [after](#rule-after) 规则一样，另一个待验证的字段名称支持作为 `date` 的值。

为方便起见，基于日期的规则也可以使用流畅的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->before(today()->subDays(7)),
],
```

`beforeToday` 和 `todayOrBefore` 方法可以分别用来流利地表示日期必须在今天之前或今天或之前：

```php
'start_date' => [
    'required',
    Rule::date()->beforeToday(),
],
```

<a name="rule-before-or-equal"></a>
#### before\_or\_equal:_date_

待验证字段的值对应的日期必须在给定的日期之前或等于被给定的日期。这个日期将被传递给 PHP 函数 `strtotime` 以便转化为有效的 `DateTime` 实例。此外，像 [after](#rule-after) 规则一样，另一个待验证的字段名称支持作为 `date` 的值。

为方便起见，基于日期的规则也可以使用流畅的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->beforeOrEqual(today()->subDays(7)),
],
```



<a name="rule-between"></a>
#### between:_min_,_max_

待验证字段值的大小必须介于给定的最小值和最大值（含）之间。 字符串、数字、数组和文件的计算方式与 [size](#rule-size) 规则相同.

<a name="rule-boolean"></a>
#### boolean

待验证的字段必须能够转换为布尔值。可接受的输入有 `true` , `false` , `1` , `0` , `「1」` , 和 `「0」` 。

<a name="rule-confirmed"></a>
#### confirmed

需要验证的字段必须有一个匹配的字段 `{field}_confirmation` 。例如，如果验证的字段是  `password` ，则必须在输入中出现一个匹配的 `password_confirmation` 字段。

您还可以传递一个自定义确认字段名。例如， `confirmed:repeat_username` 将期望字段  `repeat_username` 与正在验证的字段匹配。

<a name="rule-contains"></a>
#### contains:_foo_,_bar_,...

验证的字段必须是包含所有给定参数值的数组。由于该规则经常要求您 `implode` 一个数组，所以可以使用 `rule::contains` 方法来流畅地构造该规则：

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

<a name="rule-current-password"></a>
#### current_password

待验证下的字段必须与已经过身份验证的用户密码匹配。您可以指定一个 [授权门禁](/docs/laravel/12.x/authentication) ，使用规则的第一个参数：

```php
'password' => 'current_password:api'
```

<a name="rule-date"></a>
#### date

根据PHP函数 `strtotime` ，验证下的字段必须是一个有效的非相对日期。

<a name="rule-date-equals"></a>
#### date_equals:_date_



验证中的字段必须等于给定的日期。日期将被传递到 PHP  `strtotime` 函数中，以便转换为有效的 `DateTime` 实例。

<a name="rule-date-format"></a>
#### date_format:_format_,...

验证的字段必须匹配给定的 formats 之一。在验证字段时，应该使用 `date` 或  `date_format` 中的 **其中一个** ，而不是同时使用。该验证规则支持 PHP [DateTime](https://www.php.net/manual/en/class.datetime.php) 类所支持的所有格式。

为方便起见，基于日期的规则可以使用流畅的 `date` 规则构建器来构建：

```php
use Illuminate\Validation\Rule;

'start_date' => [
    'required',
    Rule::date()->format('Y-m-d'),
],
```

<a name="rule-decimal"></a>
#### decimal:_min_,_max_

验证的字段必须是数字并且必须包含指定数量的小数位：

```php
// 必须有两位小数 (9.99)...
'price' => 'decimal:2'

// 必须在2到4位小数之间...
'price' => 'decimal:2,4'
```

<a name="rule-declined"></a>
#### declined

验证的字段必须是 `「no」` , `「off」` , `0` , `「0」` , `false` , 或 `「false」` 。

<a name="rule-declined-if"></a>
#### declined_if:anotherfield,value,...

如果另一个验证字段的值等于指定值，则验证字段的值必须为 `「no」` , `「off」` , `0` , `「0」` , `false` , 或 `「false」` 。

<a name="rule-different"></a>
#### different:_field_

验证的字段必须与 field 有不同的值。

<a name="rule-digits"></a>
#### digits:_value_

验证的整数必须具有确切的 value 长度。

<a name="rule-digits-between"></a>
#### digits_between:_min_,_max_

验证的整数长度必须在给定的 min 和 max 之间。



#### dimensions

被验证的文件必须是符合规则参数中指定的尺寸约束的图片：

```php
'avatar' => 'dimensions:min_width=100,min_height=200'
```

可用的约束有：*min_width*、*max_width*、*min_height*、*max_height*、*width*、*height*、*ratio*。

*ratio* 约束应表示为宽度除以高度。它既可以用分数表示，例如 `3/2`，也可以用浮点数表示，例如 `1.5`：

```php
'avatar' => 'dimensions:ratio=3/2'
```

由于此规则需要多个参数，因此通常更方便使用 `Rule::dimensions` 方法以流式方式构建规则：

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

#### distinct

在验证数组时，被验证的字段不能有任何重复的值：

```php
'foo.*.id' => 'distinct'
```

`distinct` 默认使用宽松的变量比较。要使用严格比较，可以在验证规则定义中添加 `strict` 参数：

```php
'foo.*.id' => 'distinct:strict'
```

你可以在验证规则参数中添加 `ignore_case` 来让规则忽略大小写差异：

```php
'foo.*.id' => 'distinct:ignore_case'
```

#### doesnt_start_with:_foo_,_bar_,...

被验证的字段不能以给定值之一开头。

#### doesnt_end_with:_foo_,_bar_,...

被验证的字段不能以给定值之一结尾。

#### email

被验证的字段必须是电子邮件地址格式。此验证规则使用 [egulias/email-validator](https://github.com/egulias/EmailValidator) 包来验证电子邮件地址。默认情况下，应用的是 `RFCValidation` 验证器，但你也可以应用其他验证方式：

```php
'email' => 'email:rfc,dns'
```



上面的示例将应用 `RFCValidation` 和 `DNSCheckValidation` 验证。下面是可以应用的完整验证类型列表：

<div class="content-list" markdown="1">

-   `rfc`：`RFCValidation` — 根据[支持的 RFC](https://github.com/egulias/EmailValidator?tab=readme-ov-file#supported-rfcs)验证电子邮件地址。
    -   `strict`：`NoRFCWarningsValidation` — 根据[支持的 RFC](https://github.com/egulias/EmailValidator?tab=readme-ov-file#supported-rfcs)验证电子邮件，如果发现警告（例如末尾有点、连续多个点）则验证失败。
    -   `dns`：`DNSCheckValidation` — 确保电子邮件地址的域名有有效的 MX 记录。
    -   `spoof`：`SpoofCheckValidation` — 确保电子邮件地址不包含同形或欺骗性的 Unicode 字符。
    -   `filter`：`FilterEmailValidation` — 根据 PHP 的 `filter_var` 函数验证电子邮件地址是否合法。
    -   `filter_unicode`：`FilterEmailValidation::unicode()` — 根据 PHP 的 `filter_var` 函数验证电子邮件地址是否合法，同时允许某些 Unicode 字符。

</div>

为了方便，电子邮件验证规则可以使用流式规则构建器：

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

> [!警告]
> `dns` 和 `spoof` 验证器需要 PHP 的 `intl` 扩展。

#### ends_with:_foo_,_bar_,...

被验证的字段必须以给定的某个值结尾。

#### enum

`Enum` 规则是一个基于类的规则，用于验证字段的值是否是有效的枚举值。`Enum` 规则的构造函数只接受枚举的名称。当验证原始值时，应提供一个“backed Enum”给 `Enum` 规则：

```php
use App\Enums\ServerStatus;
use Illuminate\Validation\Rule;

$request->validate([
    'status' => [Rule::enum(ServerStatus::class)],
]);
```



`Enum` 规则的 `only` 和 `except` 方法可以用来限制哪些枚举项应被视为有效：

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

#### exclude

被验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

#### exclude_if:_anotherfield_,_value_

如果字段 *anotherfield* 的值等于 *value*，则被验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

如果需要更复杂的条件排除逻辑，可以使用 `Rule::excludeIf` 方法。此方法接受布尔值或闭包。当传入闭包时，闭包应返回 `true` 或 `false` 来指示被验证字段是否应被排除：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => Rule::excludeIf($request->user()->is_admin),
]);

Validator::make($request->all(), [
    'role_id' => Rule::excludeIf(fn () => $request->user()->is_admin),
]);
```

#### exclude_unless:_anotherfield_,_value_

除非字段 *anotherfield* 的值等于 *value*，否则被验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。如果 *value* 为 `null`（例如 `exclude_unless:name,null`），则除非比较字段为 `null` 或请求数据中没有该比较字段，否则被验证的字段将被排除。



#### exclude_with:_anotherfield_

如果字段 *anotherfield* 存在，则被验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

#### exclude_without:_anotherfield_

如果字段 *anotherfield* 不存在，则被验证的字段将从 `validate` 和 `validated` 方法返回的请求数据中排除。

#### exists:_table_,_column_

被验证的字段必须存在于指定的数据库表中。

#### Basic Usage of Exists Rule

```php
'state' => 'exists:states'
```

如果未指定 `column` 选项，则将使用字段名。因此在此示例中，该规则将验证 `states` 数据库表中是否存在一条记录，其 `state` 列的值与请求中的 `state` 属性值匹配。

#### 指定自定义列名

你可以在数据库表名之后明确指定应使用的数据库列名：

```php
'state' => 'exists:states,abbreviation'
```

有时，你可能需要为 `exists` 查询指定特定的数据库连接。你可以通过在表名前加上连接名来实现：

```php
'email' => 'exists:connection.staff,email'
```

你也可以不直接指定表名，而是指定用于确定表名的 Eloquent 模型：

```php
'user_id' => 'exists:App\Models\User,id'
```

如果你想自定义验证规则执行的查询，可以使用 `Rule` 类来流畅地定义规则。在此示例中，我们还将验证规则作为数组指定，而不是使用 `|` 字符分隔：

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



你可以通过在 `Rule::exists` 方法中提供列名作为第二个参数，明确指定 `exists` 规则应使用的数据库列名：

```php
'state' => Rule::exists('states', 'abbreviation'),
```

有时，你可能希望验证一个值数组是否存在于数据库中。可以通过为被验证字段添加 `exists` 和 [array](#rule-array) 规则来实现：

```php
'states' => ['array', Rule::exists('states', 'abbreviation')],
```

当这两个规则都分配给一个字段时，Laravel 会自动构建单条查询，以确定指定表中是否存在所有给定的值。

#### extensions:_foo_,_bar_,...

被验证的文件必须具有用户指定的扩展名，并且该扩展名应在列出的扩展名中：

```php
'photo' => ['required', 'extensions:jpg,png'],
```

> [!警告]
> 你不应该仅依赖文件的用户指定扩展名进行验证。此规则通常应与 [mimes](#rule-mimes) 或 [mimetypes](#rule-mimetypes) 规则结合使用。

#### file

被验证的字段必须是成功上传的文件。

#### filled

当字段存在时，被验证的字段不能为空。

#### gt:_field_

被验证的字段必须大于指定的 *field* 或 *value*。这两个字段必须类型相同。字符串、数字、数组和文件的评估方式与 [size](#rule-size) 规则相同。



#### gte:_field_

被验证的字段必须大于或等于指定的 *field* 或 *value*。这两个字段必须类型相同。字符串、数字、数组和文件的评估方式与 [size](#rule-size) 规则相同。

#### hex_color

被验证的字段必须包含有效的 [十六进制](https://developer.mozilla.org/en-US/docs/Web/CSS/hex-color) 颜色值。

#### image

被验证的文件必须是图像（jpg、jpeg、png、bmp、gif 或 webp）。

> [!警告]
> 默认情况下，image 规则不允许 SVG 文件，因为存在 XSS 漏洞的可能性。如果需要允许 SVG 文件，可以向 image 规则提供 `allow_svg` 指令（`image:allow_svg`）。

#### in:_foo_,_bar_,...

被验证的字段必须包含在给定的值列表中。由于此规则通常需要对数组进行 `implode` 操作，因此可以使用 `Rule::in` 方法来流畅地构建规则：

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

当 `in` 规则与 `array` 规则结合使用时，输入数组中的每个值都必须存在于 `in` 规则提供的值列表中。在下面的示例中，输入数组中的 `LAS` 机场代码无效，因为它不在 `in` 规则提供的机场列表中：

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



#### in_array:_anotherfield_.*

被验证的字段必须存在于 *anotherfield* 的值中。

#### in_array_keys:_value_.*

被验证的字段必须是一个数组，且数组中至少有一个键为给定的 *values*：

```php
'config' => 'array|in_array_keys:timezone'
```

#### integer

被验证的字段必须是一个整数。

> [!警告]
> 该验证规则并不检查输入是否为“integer”类型变量，仅验证输入是否符合 PHP 的 `FILTER_VALIDATE_INT` 规则可接受的类型。如果需要验证输入确实为数字，请将此规则与 [numeric 验证规则](#rule-numeric) 结合使用。

#### ip

被验证的字段必须是一个 IP 地址。

#### ipv4

被验证的字段必须是一个 IPv4 地址。

#### ipv6

被验证的字段必须是一个 IPv6 地址。

#### json

被验证的字段必须是一个有效的 JSON 字符串。

#### lt:_field_

被验证的字段必须小于指定的 *field*。这两个字段必须类型相同。字符串、数字、数组和文件的评估方式与 [size](#rule-size) 规则相同。

#### lte:_field_

被验证的字段必须小于或等于指定的 *field*。这两个字段必须类型相同。字符串、数字、数组和文件的评估方式与 [size](#rule-size) 规则相同。



#### lowercase

被验证的字段必须为小写字母。

#### list

被验证的字段必须是一个数组，并且该数组必须是一个列表。
当数组的键从 0 到 `count($array) - 1` 连续编号时，该数组才被视为列表。

#### mac_address

被验证的字段必须是一个 MAC 地址。

#### max:_value_

被验证的字段必须小于或等于指定的最大值 *value*。
字符串、数字、数组和文件的验证方式与 [size](#rule-size) 规则相同。

#### max_digits:_value_

被验证的整数的数字长度不能超过 *value*。

#### mimetypes:_text/plain_,...

被验证的文件必须匹配给定的 MIME 类型之一：

```php
'video' => 'mimetypes:video/avi,video/mpeg,video/quicktime'
```

在确定上传文件的 MIME 类型时，系统会读取文件内容并尝试推断实际的 MIME 类型，这个类型可能与客户端提供的 MIME 类型不同。

#### mimes:_foo_,_bar_,...

被验证的文件必须具有与列出的扩展名对应的 MIME 类型：

```php
'photo' => 'mimes:jpg,bmp,png'
```

虽然只需要指定文件扩展名，但该规则实际上会读取文件内容来验证其 MIME 类型。
完整的 MIME 类型及其对应扩展名列表可在以下位置找到：



[https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types](https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types)

#### MIME Types and Extensions

此验证规则不会检查 MIME 类型与用户为文件指定的扩展名是否一致。
例如，`mimes:png` 验证规则会认为一个包含有效 PNG 内容的文件是合法的 PNG 图片，即使该文件名为 `photo.txt`。
如果你希望验证用户指定的文件扩展名，可以使用 [extensions](#rule-extensions) 规则。

#### min:_value_

被验证的字段必须具有最小值 *value*。
字符串、数字、数组和文件的验证方式与 [size](#rule-size) 规则相同。

#### min_digits:*value*

被验证的整数的数字长度必须至少为 *value*。

#### multiple_of:*value*

被验证的字段必须是 *value* 的倍数。

#### missing

被验证的字段在输入数据中必须不存在。

#### missing_if:*anotherfield*,*value*,...

当 *anotherfield* 字段的值等于任意一个 *value* 时，被验证的字段必须不存在。

#### missing_unless:*anotherfield*,*value*

除非 *anotherfield* 字段的值等于任意一个 *value*，否则被验证的字段必须不存在。

#### missing_with:*foo*,*bar*,...

当任意一个指定的其他字段存在时，被验证的字段必须不存在。



#### missing_with_all:*foo*,*bar*,...

只有当所有其他指定的字段都存在时，被验证的字段才必须不存在。

#### not_in:*foo*,*bar*,...

被验证的字段的值不能包含在给定的值列表中。
可以使用 `Rule::notIn` 方法以更流畅的方式构建此规则：

```php
use Illuminate\Validation\Rule;

Validator::make($data, [
    'toppings' => [
        'required',
        Rule::notIn(['sprinkles', 'cherries']),
    ],
]);
```

#### not_regex:*pattern*

被验证的字段值不得匹配给定的正则表达式。

在内部，此规则使用 PHP 的 `preg_match` 函数。
所指定的正则表达式模式应符合 `preg_match` 所要求的格式，并包含有效的分隔符。
例如：`'email' => 'not_regex:/^.+$/i'`。

> [!WARNING]
> 在使用 `regex` / `not_regex` 模式时，如果正则表达式中包含 `|` 字符，可能需要使用数组语法来定义验证规则，而不是使用 `|` 分隔符。

#### nullable

被验证的字段可以为 `null`。

#### numeric

被验证的字段必须是[数值型](https://www.php.net/manual/en/function.is-numeric.php)。

#### present

被验证的字段必须存在于输入数据中。

#### present_if:*anotherfield*,*value*,...

当 *anotherfield* 字段的值等于任意一个 *value* 时，被验证的字段必须存在。

#### present_unless:*anotherfield*,*value*

除非 *anotherfield* 字段的值等于任意一个 *value*，否则被验证的字段必须存在。



#### present_with:*foo*,*bar*,...

只有当任意一个指定的其他字段存在时，被验证的字段才必须存在。

#### present_with_all:*foo*,*bar*,...

只有当所有其他指定的字段都存在时，被验证的字段才必须存在。

#### prohibited

被验证的字段必须缺失或为空。
字段被视为“空”的情况包括以下任意一种：

<div class="content-list" markdown="1">

- The value is `null`.
- The value is an empty string.
- The value is an empty array or empty `Countable` object.
- The value is an uploaded file with an empty path.

</div>

#### prohibited_if:*anotherfield*,*value*,...

当 *anotherfield* 字段的值等于任意一个 *value* 时，被验证的字段必须缺失或为空。
字段被视为“空”的情况包括以下任意一种：

<div class="content-list" markdown="1">

- The value is `null`.
- The value is an empty string.
- The value is an empty array or empty `Countable` object.
- The value is an uploaded file with an empty path.

</div>

如果需要更复杂的条件禁用逻辑，可以使用 `Rule::prohibitedIf` 方法。
此方法接受一个布尔值或闭包（closure）。当传入闭包时，闭包应返回 `true` 或 `false`，以指示该字段是否应被禁止：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => Rule::prohibitedIf($request->user()->is_admin),
]);

Validator::make($request->all(), [
    'role_id' => Rule::prohibitedIf(fn () => $request->user()->is_admin),
]);
```


#### prohibited_if_accepted:*anotherfield*,...

当 *anotherfield* 字段的值等于 `"yes"`、`"on"`、`1`、`"1"`、`true` 或 `"true"` 时，被验证的字段必须缺失或为空。

#### prohibited_if_declined:*anotherfield*,...

当 *anotherfield* 字段的值等于 `"no"`、`"off"`、`0`、`"0"`、`false` 或 `"false"` 时，被验证的字段必须缺失或为空。

#### prohibited_unless:*anotherfield*,*value*,...

除非 *anotherfield* 字段的值等于任意一个 *value*，否则被验证的字段必须缺失或为空。
字段被视为“空”的情况包括以下任意一种：

<div class="content-list" markdown="1">

-   值为 `null`。
-   值为空字符串。
-   值为空数组或空的 `Countable` 对象。
-   值为一个上传文件且其路径为空。

</div>

#### prohibits:_anotherfield_,...

如果被验证的字段存在且不为空，那么 *anotherfield* 中的所有字段都必须缺失或为空。
字段被视为“空”的情况包括以下任意一种：

<div class="content-list" markdown="1">

- The value is `null`.
- The value is an empty string.
- The value is an empty array or empty `Countable` object.
- The value is an uploaded file with an empty path.

</div>

#### regex:_pattern_

被验证的字段必须匹配给定的正则表达式。

在内部，此规则使用 PHP 的 `preg_match` 函数。
指定的正则表达式模式必须遵循 `preg_match` 所要求的格式，并且必须包含有效的分隔符。
例如：`'email' => 'regex:/^.+@.+$/i'`。

> [!警告]
> 当使用 `regex` / `not_regex` 模式时，如果正则表达式中包含 `|` 字符，可能需要使用数组语法定义规则，而不是使用 `|` 分隔符。



#### required

被验证的字段必须在输入数据中存在且不能为空。
一个字段被认为是“空”的情况包括以下几种：

<div class="content-list" markdown="1">

-   该值为 `null`；
-   该值是一个空字符串；
-   该值是一个空数组或空的 `Countable` 对象；
-   该值是一个没有路径的已上传文件。

</div>

#### required_if:_anotherfield_,_value_,...

当 ***anotherfield*** 字段的值等于任意一个指定的 ***value*** 时，被验证的字段必须存在且不能为空。

如果你希望为 `required_if` 规则构造更复杂的条件，可以使用 `Rule::requiredIf` 方法。
此方法接收一个布尔值或闭包。当传入闭包时，闭包应返回 `true` 或 `false`，以指示该字段是否为必填字段：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

Validator::make($request->all(), [
    'role_id' => Rule::requiredIf($request->user()->is_admin),
]);

Validator::make($request->all(), [
    'role_id' => Rule::requiredIf(fn () => $request->user()->is_admin),
]);
```

#### required_if_accepted:_anotherfield_,...

当 ***anotherfield*** 字段的值等于 `"yes"`、`"on"`、`1`、`"1"`、`true` 或 `"true"` 时，被验证的字段必须存在且不能为空。

#### required_if_declined:_anotherfield_,...

当 ***anotherfield*** 字段的值等于 `"no"`、`"off"`、`0`、`"0"`、`false` 或 `"false"` 时，被验证的字段必须存在且不能为空。

#### required_unless:_anotherfield_,_value_,...



除非 ***anotherfield*** 字段的值等于任意一个指定的 ***value***，否则被验证的字段必须存在且不能为空。
这也意味着，除非 ***value*** 为 `null`，否则 ***anotherfield*** 字段必须在请求数据中存在。
如果 ***value*** 是 `null`（例如：`required_unless:name,null`），则被验证的字段在以下情况下是必填的：
当对比字段的值为 `null` 或者对比字段在请求数据中缺失时，该字段必须存在且不能为空。

#### required_with:_foo_,_bar_,...

只有当任意一个指定的其他字段存在且不为空时，被验证的字段才必须存在且不能为空。

#### required_with_all:_foo_,_bar_,...

只有当所有指定的其他字段都存在且不为空时，被验证的字段才必须存在且不能为空。

#### required_without:_foo_,_bar_,...

只有当任意一个指定的其他字段为空或不存在时，被验证的字段才必须存在且不能为空。

#### required_without_all:_foo_,_bar_,...

只有当所有指定的其他字段都为空或不存在时，被验证的字段才必须存在且不能为空。

#### required_array_keys:_foo_,_bar_,...

被验证的字段必须是一个数组，并且该数组中必须至少包含指定的键名。

#### same:_field_

给定的 ***field*** 字段的值必须与被验证字段的值完全相同。

#### size:_value_

被验证字段的大小必须与给定的 ***value*** 相匹配。
对于不同类型的数据，`size` 的含义不同：

-   **字符串**：`value` 表示字符数；
-   **数字**：`value` 表示数值大小（该字段还必须有 `numeric` 或 `integer` 验证规则）；
-   **数组**：`value` 表示数组的元素数量；
-   **文件**：`value` 表示文件大小（以 **KB** 为单位）。

示例：

```php
// 验证字符串长度必须正好为 12 个字符...
'title' => 'size:12';

// 验证整数值必须等于 10...
'seats' => 'integer|size:10';

// 验证数组必须正好包含 5 个元素...
'tags' => 'array|size:5';

// 验证上传文件的大小必须正好为 512 KB...
'image' => 'file|size:512';
```



#### starts_with:_foo_,_bar_,...

被验证的字段的值必须以指定的任意一个值作为开头。

#### string

被验证的字段必须是一个字符串。
如果希望该字段也可以为 `null`，应为该字段同时指定 `nullable` 规则。

#### timezone

被验证的字段必须是一个合法的时区标识符，该标识符需符合 `DateTimeZone::listIdentifiers` 方法的定义。

此验证规则还可以接收与 [`DateTimeZone::listIdentifiers` 方法](https://www.php.net/manual/en/datetimezone.listidentifiers.php) 相同的参数，例如：

```php
'timezone' => 'required|timezone:all';

'timezone' => 'required|timezone:Africa';

'timezone' => 'required|timezone:per_country,US';
```

#### unique:_table_,_column_

被验证的字段的值在指定的数据表中必须是唯一的（即该值在数据库表中不能已存在）。

**指定自定义表 / 列名：**

除了直接指定表名外，你也可以通过 Eloquent 模型来确定表名，例如：

```php
'email' => 'unique:App\Models\User,email_address'
```

`column` 参数可用于指定该字段在数据库中对应的列名。
如果未指定 `column` 参数，则默认使用被验证字段的名称作为列名。

```php
'email' => 'unique:users,email_address'
```

**指定自定义数据库连接：**

有时你可能需要为验证器的数据库查询设置自定义连接。
要实现这一点，可以在表名前添加连接名称：

```php
'email' => 'unique:connection.users,email_address'
```

**强制唯一规则忽略指定的 ID：**



有时，在执行唯一性验证（`unique`）时，你可能希望忽略某个特定的 ID。
例如，假设你有一个“更新个人资料”的页面，其中包含用户的姓名、电子邮箱和所在地。
通常，你希望验证电子邮箱地址是唯一的。
然而，如果用户仅修改了姓名而没有更改电子邮箱，你并不希望抛出验证错误，因为该电子邮箱本就是该用户自己的。

为让验证器在验证时忽略当前用户的 ID，我们可以使用 `Rule` 类以流式方式定义规则。
在下面的示例中，我们还使用数组形式来定义验证规则，而不是用 `|` 字符分隔：

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

> [!警告]
> 切勿将用户可控的请求输入直接传递给 `ignore` 方法。
> 你应该只传递系统生成的唯一 ID，例如来自 Eloquent 模型实例的自增 ID 或 UUID。
> 否则，你的应用程序将面临 SQL 注入攻击的风险。

除了传递模型主键的值给 `ignore` 方法外，你也可以直接传递整个模型实例。
Laravel 会自动从模型中提取主键值：

```php
Rule::unique('users')->ignore($user)
```

如果你的数据表使用的主键列名不是 `id`，则可以在调用 `ignore` 方法时显式指定该列名：

```php
Rule::unique('users')->ignore($user->id, 'user_id')
```



默认情况下，`unique` 规则会检查与被验证属性同名的列是否唯一。
但是，你可以通过向 `unique` 方法传递第二个参数来自定义要检查的列名：

```php
Rule::unique('users', 'email_address')->ignore($user->id)
```

**添加额外的 Where 条件：**

你可以使用 `where` 方法自定义查询条件，以指定更多的查询约束。
例如，下面的示例中，我们添加了一个查询条件，仅在 `account_id` 为 `1` 的记录中检查唯一性：

```php
'email' => Rule::unique('users')->where(fn (Builder $query) => $query->where('account_id', 1))
```

**在唯一性检查中忽略软删除（Soft Delete）记录：**

默认情况下，`unique` 规则在执行唯一性验证时会包含被软删除的记录。
若要在验证时排除软删除的记录，可以调用 `withoutTrashed` 方法：

```php
Rule::unique('users')->withoutTrashed();
```

如果你的模型使用的软删除字段名称不是 `deleted_at`，可以在调用 `withoutTrashed` 方法时指定该列名：

```php
Rule::unique('users')->withoutTrashed('was_deleted_at');
```

#### uppercase

被验证的字段的值必须为全大写形式。

#### url

被验证的字段的值必须是一个有效的 URL。

如果你希望指定允许的 URL 协议，可以将协议名称作为验证规则参数传入：

```php
'url' => 'url:http,https',

'game' => 'url:minecraft,steam',
```

#### ulid

被验证的字段必须是一个有效的 [通用唯一可排序标识符（ULID）](https://github.com/ulid/spec)。



#### uuid

被验证的字段必须是一个符合 **RFC 9562** 标准（版本 1、3、4、5、6、7 或 8）的 **通用唯一标识符（UUID）**。

你还可以通过指定版本号，验证给定的 UUID 是否符合特定版本的规范：

```php
'uuid' => 'uuid:4'
```

## 条件性添加规则

#### 当字段具有特定值时跳过验证

有时，你可能希望在某个字段具有特定值时，不对另一个字段进行验证。
可以使用 `exclude_if` 验证规则来实现此目的。

在以下示例中，当 `has_appointment` 字段的值为 `false` 时，`appointment_date` 和 `doctor_name` 字段将不会被验证：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($data, [
    'has_appointment' => 'required|boolean',
    'appointment_date' => 'exclude_if:has_appointment,false|required|date',
    'doctor_name' => 'exclude_if:has_appointment,false|required|string',
]);
```

或者，你也可以使用 `exclude_unless` 规则，使某个字段 **仅当** 另一个字段具有特定值时才进行验证：

```php
$validator = Validator::make($data, [
    'has_appointment' => 'required|boolean',
    'appointment_date' => 'exclude_unless:has_appointment,true|required|date',
    'doctor_name' => 'exclude_unless:has_appointment,true|required|string',
]);
```

#### 当字段存在时进行验证

在某些情况下，你可能希望 **仅在某个字段存在于被验证的数据中时** 才执行验证规则。
可以通过在规则列表中添加 `sometimes` 规则来快速实现：

```php
$validator = Validator::make($data, [
    'email' => 'sometimes|required|email',
]);
```

在上面的示例中，`email` 字段仅在它存在于 `$data` 数组中时才会被验证。

> [!注意]
> 如果你要验证的字段应当始终存在，但可以为空，请参阅[关于可选字段的说明](#a-note-on-optional-fields)。



#### 复杂条件验证

有时候，你可能希望根据更复杂的条件逻辑来添加验证规则。
例如，当另一个字段的值大于 100 时，你可能希望要求某个字段是必填的；
或者，当某个字段存在时，你可能希望另外两个字段必须具有特定的值。

要实现这些条件验证并不困难。首先，使用那些**始终适用的静态规则**创建一个 `Validator` 实例：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($request->all(), [
    'email' => 'required|email',
    'games' => 'required|integer|min:0',
]);
```

假设我们的网页应用是为游戏收藏者设计的。
如果一位收藏者在注册时表示他拥有超过 100 个游戏，我们希望他解释一下为什么会有这么多游戏。
例如，也许他经营一家游戏转售店，或者他只是单纯喜欢收藏游戏。

要有条件地添加这个要求，我们可以在 `Validator` 实例上使用 `sometimes` 方法：

```php
use Illuminate\Support\Fluent;

$validator->sometimes('reason', 'required|max:500', function (Fluent $input) {
    return $input->games >= 100;
});
```

传给 `sometimes` 方法的第一个参数是**要进行条件验证的字段名**，
第二个参数是**要添加的验证规则**，
第三个参数是一个闭包（函数），当该函数返回 `true` 时，这些规则就会被应用。

这种方式让编写复杂的条件验证变得非常轻松。
你甚至可以一次为多个字段添加条件验证，例如：

```php
$validator->sometimes(['reason', 'cost'], 'required', function (Fluent $input) {
    return $input->games >= 100;
});
```

> [!注意]
> 传入闭包的 `$input` 参数是 `Illuminate\Support\Fluent` 的实例，
你可以使用它来访问正在被验证的输入数据和文件。



#### 复杂条件数组验证

有时候，你可能希望根据同一个嵌套数组中**另一个字段的值**来验证某个字段，
但你**并不知道这个字段的具体索引**。

在这种情况下，你可以让闭包（回调函数）接收**第二个参数**，
该参数表示当前正在被验证的**数组项**：

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

就像传给闭包的 `$input` 参数一样，
当被验证的属性数据是数组时，`$item` 参数也是 `Illuminate\Support\Fluent` 的实例；
如果该属性不是数组，那么 `$item` 就是一个字符串。

## 验证数组

正如 [array 验证规则文档](#rule-array) 中所述，
`array` 规则可以接受一个**允许存在的键名列表**。
如果数组中包含了**未被允许的额外键名**，验证就会失败：

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
    'user' => 'array:name,username',
]);
```

一般来说，你应当始终**明确指定数组中允许的键名**。
否则，验证器的 `validate` 与 `validated` 方法会返回所有被验证的数据，
包括整个数组及其所有键，即使这些键没有通过其他嵌套的数组验证规则验证。

### 验证嵌套数组输入

验证表单中嵌套数组类型的输入字段其实并不复杂。
你可以使用**点语法（dot notation）**来验证数组中的属性。

例如，如果传入的 HTTP 请求中包含字段 `photos[profile]`，
你可以像这样进行验证：

```php
use Illuminate\Support\Facades\Validator;

$validator = Validator::make($request->all(), [
    'photos.profile' => 'required|image',
]);
```



你也可以验证数组中**每一个元素**。
例如，要验证某个数组输入字段中的每个邮箱地址都是唯一的，可以这样做：

```php
$validator = Validator::make($request->all(), [
    'person.*.email' => 'email|unique:users',
    'person.*.first_name' => 'required_with:person.*.last_name',
]);
```

同样地，在[语言文件中定义自定义验证消息](#custom-messages-for-specific-attributes)时，
你也可以使用 `*` 通配符，让数组字段共享同一个验证消息，这样会非常方便：

```php
'custom' => [
    'person.*.email' => [
        'unique' => 'Each person must have a unique email address',
    ]
],
```

#### 访问嵌套数组数据

有时，在为某个属性分配验证规则时，你可能需要**访问嵌套数组元素的值**。
这可以通过使用 `Rule::forEach` 方法来实现。

`forEach` 方法接收一个闭包，这个闭包会在每次验证数组属性时被调用，
并会接收该属性的**值**和**完整展开的属性名**作为参数。

该闭包应返回一个数组，包含要应用到该数组元素的验证规则：

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

### 错误消息中的索引与位置

在验证数组时，你可能希望在应用显示的错误消息中，
**引用出错元素在数组中的索引或位置**。

为此，你可以在[自定义验证消息](#manual-customizing-the-error-messages)中使用占位符
`:index`（从 `0` 开始）和 `:position`（从 `1` 开始）：

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
    'photos.*.description' => 'required',
], [
    'photos.*.description.required' => 'Please describe photo #:position.',
]);
```



在上面的示例中，验证将失败，并向用户显示以下错误信息：
*Please describe photo #2.*（请为第 2 张照片添加描述。）

如果需要，你还可以引用更深层级的嵌套索引或位置，
可以使用 `second-index`、`second-position`、`third-index`、`third-position` 等占位符：

```php
'photos.*.attributes.*.string' => 'Invalid attribute for photo #:second-position.',
```

## 文件验证

Laravel 提供了多种用于验证上传文件的规则，比如 `mimes`、`image`、`min` 和 `max`。
虽然你可以在验证文件时单独指定这些规则，
Laravel 还提供了一种**更简洁的文件验证规则构造器（fluent builder）**，
使用起来更加方便：

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

#### 验证文件类型

即使在调用 `types` 方法时只需指定**文件扩展名**，
Laravel 实际上是通过**读取文件内容并推测 MIME 类型**来验证文件类型的。

你可以在以下链接中找到完整的 MIME 类型与其对应扩展名的列表：

<https://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types>

#### 验证文件大小

为了方便使用，最小值和最大值的文件大小可以用带单位的字符串表示。
支持的单位后缀包括：`kb`、`mb`、`gb` 和 `tb`：

```php
File::types(['mp3', 'wav'])
    ->min('1kb')
    ->max('10mb');
```



#### 验证图像文件

如果你的应用允许用户上传图像，你可以使用 `File` 规则的 `image` 构造方法，
以确保正在验证的文件是图像（jpg、jpeg、png、bmp、gif 或 webp）。

此外，你还可以使用 `dimensions` 规则来限制图像的尺寸：

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

> [!注意]
> 有关验证图像尺寸的更多信息，请参阅 [dimension 规则文档](#rule-dimensions)。

> [!警告]
> 默认情况下，`image` 规则不允许 SVG 文件，以防止可能的 XSS 漏洞。
> 如果你需要允许 SVG 文件，可以向 `image` 规则传入 `allowSvg: true`：
> `File::image(allowSvg: true)`。

#### 验证图像尺寸

你也可以验证图像的尺寸。
例如，要验证上传的图像至少宽 1000 像素、高 500 像素，可以使用 `dimensions` 规则：

```php
use Illuminate\Validation\Rule;
use Illuminate\Validation\Rules\File;

File::image()->dimensions(
    Rule::dimensions()
        ->maxWidth(1000)
        ->maxHeight(500)
)
```

> [!注意]
> 有关验证图像尺寸的更多信息，请参阅 [dimension 规则文档](#rule-dimensions)。

## 验证密码

为了确保密码具有足够的复杂度，你可以使用 Laravel 的 `Password` 规则对象：

```php
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rules\Password;

$validator = Validator::make($request->all(), [
    'password' => ['required', 'confirmed', Password::min(8)],
]);
```



`Password` 规则对象允许你轻松自定义应用程序的密码复杂性要求，例如指定密码必须包含至少一个字母、数字、符号，或包含大小写混合字符：

```php
// 要求至少 8 个字符...
Password::min(8)

// 要求至少包含一个字母...
Password::min(8)->letters()

// 要求至少包含一个大写和一个小写字母...
Password::min(8)->mixedCase()

// 要求至少包含一个数字...
Password::min(8)->numbers()

// 要求至少包含一个符号...
Password::min(8)->symbols()
```

此外，你可以使用 `uncompromised` 方法确保密码未在公开的密码数据泄露中被泄漏：

```php
Password::min(8)->uncompromised()
```

在内部，`Password` 规则对象使用 [k-匿名性 (k-Anonymity)](https://en.wikipedia.org/wiki/K-anonymity) 模型，通过 [haveibeenpwned.com](https://haveibeenpwned.com) 服务来判断密码是否被泄露，而不会牺牲用户的隐私或安全性。

默认情况下，如果某个密码在数据泄露中出现过至少一次，就会被视为已泄露。你可以通过给 `uncompromised` 方法传入第一个参数来自定义这一阈值：

```php
// 确保密码在同一数据泄露中出现次数少于 3 次...
Password::min(8)->uncompromised(3);
```

当然，你可以将以上方法链式调用：

```php
Password::min(8)
    ->letters()
    ->mixedCase()
    ->numbers()
    ->symbols()
    ->uncompromised()
```

#### 定义默认密码规则

你可能希望在应用程序的某个集中位置定义默认的密码验证规则。你可以通过 `Password::defaults` 方法轻松实现，该方法接收一个闭包。传递给 `defaults` 方法的闭包应返回 `Password` 规则的默认配置。通常，这个 `defaults` 规则会在应用程序某个服务提供者的 `boot` 方法中调用：

```php
use Illuminate\Validation\Rules\Password;

/**
 * 启动应用程序的任何服务。
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



然后，当你想将默认规则应用到某个正在验证的密码时，可以在调用 `defaults` 方法时不传入任何参数：

```php
'password' => ['required', Password::defaults()],
```

有时，你可能希望在默认的密码验证规则基础上附加额外的验证规则。你可以使用 `rules` 方法来实现：

```php
use App\Rules\ZxcvbnRule;

Password::defaults(function () {
    $rule = Password::min(8)->rules([new ZxcvbnRule]);

    // ...
});
```

## 自定义验证规则

### 使用规则对象（Rule Objects）

Laravel 提供了多种有用的验证规则；不过，你也可以自定义属于你自己的规则。
注册自定义验证规则的一种方式是使用**规则对象（Rule Objects）**。

要生成一个新的规则对象，你可以使用 `make:rule` Artisan 命令。
我们来用这个命令创建一个用于验证字符串是否为大写的规则。
Laravel 会将新规则放在 `app/Rules` 目录下；如果该目录不存在，Laravel 会在你执行命令时自动创建它：

```shell
php artisan make:rule Uppercase
```

创建好规则后，我们就可以定义它的具体行为了。
规则对象包含一个名为 `validate` 的方法。
该方法会接收属性名称、属性值，以及一个在验证失败时应被调用的回调函数（该回调会带上验证错误消息）：

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class Uppercase implements ValidationRule
{
    /**
     * 执行验证规则。
     */
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (strtoupper($value) !== $value) {
            $fail('The :attribute must be uppercase.');
        }
    }
}
```



定义好规则后，你可以通过将规则对象的实例与其他验证规则一起传递给验证器，从而将其附加到验证中：

```php
use App\Rules\Uppercase;

$request->validate([
    'name' => ['required', 'string', new Uppercase],
]);
```

#### 翻译验证消息（Translating Validation Messages）

与其在 `$fail` 闭包中直接提供字面量错误信息，你也可以提供一个[翻译字符串键](/docs/laravel/12.x/localization)，让 Laravel 来翻译错误消息：

```php
if (strtoupper($value) !== $value) {
    $fail('validation.uppercase')->translate();
}
```

如果需要，你还可以为 `translate` 方法提供占位符替换项（作为第一个参数）以及首选语言（作为第二个参数）：

```php
$fail('validation.location')->translate([
    'value' => $this->value,
], 'fr');
```

#### 访问附加数据（Accessing Additional Data）

如果你的自定义验证规则类需要访问正在被验证的所有其他数据，可以让你的规则类实现 `Illuminate\Contracts\Validation\DataAwareRule` 接口。
该接口要求类中定义一个 `setData` 方法。Laravel 会在验证开始之前自动调用该方法，并将所有正在验证的数据传入其中：

```php
<?php

namespace App\Rules;

use Illuminate\Contracts\Validation\DataAwareRule;
use Illuminate\Contracts\Validation\ValidationRule;

class Uppercase implements DataAwareRule, ValidationRule
{
    /**
     * 所有正在被验证的数据。
     *
     * @var array<string, mixed>
     */
    protected $data = [];

    // ...

    /**
     * 设置正在被验证的数据。
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

或者，如果你的验证规则需要访问执行验证的验证器实例，可以实现 `ValidatorAwareRule` 接口：

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
     * 设置当前的验证器。
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

如果您在整个应用程序中只需要使用一次自定义规则的功能，那么可以使用闭包而不是规则对象。闭包会接收属性的名称、属性的值和一个 `$fail` 回调函数，如果验证失败，则应调用该回调函数：

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

默认情况下，当待验证的属性不存在或包含空字符串时，包括自定义规则在内的常规验证规则将不会运行。例如 [unique](#rule-unique) 规则将不会对空字符串运行：

```php
use Illuminate\Support\Facades\Validator;

$rules = ['name' => 'unique:users,name'];

$input = ['name' => ''];

Validator::make($input, $rules)->passes(); // true
```

为了让自定义规则在属性为空时也能运行，该规则必须暗示该属性是必需的。要快速生成新的隐式规则对象，您可以使用带有`--implicit`选项的 `make:rule` Artisan 命令:

```shell
php artisan make:rule Uppercase --implicit
```

> [!警告]
> "隐式" 规则仅有 _implies_ 属性是必须的。至于它是否真的会因为缺少或空属性而无效，则取决于你。
