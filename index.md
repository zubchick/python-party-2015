---

layout: default

---

# Яндекс

## **{{ site.presentation.title }}** {#cover}

<div class="s">
</div>

{% if site.presentation.nda %}
<div class="nda"></div>
{% endif %}

<div class="info">
	<p class="author">{{ site.author.name }}, <br/> {{ site.author.position }}</p>
</div>

## О чем доклад
* Два слова о парсерах
    * Что такое
* Где применить
  * Конфиги
  * Языки разметки
  * Язык программирования
  * DSL
* О чем не буду рассказывать
    * Теория
    * Естественные языки

## Примеры языков запросов
* SQL
* Cypher (Neo4j)
* XPath
* Язык запросов к Яндексу

## Задача
* Есть пользователь
* Есть монга
* Нет доверия
* Нет любви


## Синтаксис

{% highlight sql %}
author=zubchick AND title~=test OR created>=today()
{% endhighlight %}

{% highlight sql %}
(author=me() OR author=test_user) AND created="19-08-2015" AND type=bug
{% endhighlight %}


## Почему бы не написать пару регулярок
* Кто же вас остановит
* Но это не будет работать
* Это трудно поддерживать
* Трудно расширять


## Шаги
* Лексический анализ
* Парсинг
    * Промежуточное дерево разбора
    * Абстрактное синтаксическое дерево
* Компиляция

## Инструменты
* funcparserlib.lexer
* funcparserlib.parser

<a href="https://github.com/vlasovskikh/funcparserlib">
https://github.com/vlasovskikh/funcparserlib
</a>
<br>
python 2 и 3


## Пишем свой парсер
{:.section}

### Лексический анализ


## Составные части

### Логические операторы
<pre><code class="language-sql" data-lang="sql">author=zubchick <span class="o">AND</span> title~=test <span class="o">OR</span> created>=today()
</code></pre>

* <code>AND</code>
* <code>OR</code>

## Составные части

### Операторы сравнения
<pre><code class="language-sql" data-lang="sql">author<span class="o">=</span>zubchick AND title<span class="o">~=</span>test OR created<span class="o">>=</span>today()
</code></pre>
* <code>~=</code>
* <code>&gt;=</code>
* <code>&lt;=</code>
* <code>=</code>
* <code>@=</code>
* etc.

## Составные части

### Имена полей
<pre><code class="language-sql" data-lang="sql"><span
class="o">author</span>=zubchick AND <span class="o">title</span>~=test OR <span class="o">created</span>>=today()
</code></pre>

## Составные части

### Текст в кавычках и без
<pre><code class="language-sql" data-lang="sql">author=<span
class="o">zubchick</span> AND title~=<span class="o">test</span> OR created>=today()
</code></pre>


<pre><code class="language-sql" data-lang="sql">(author=me() OR author=<span
class="o">test_user</span>) AND created=<span class="o">"19-08-2015"</span> AND type=<span class="o">bug</span>
</code></pre>


## Составные части

### Функции
<pre><code class="language-sql" data-lang="sql">author=zubchick AND title~=test OR created>=<span class="o">today()</span>
</code></pre>

<pre><code class="language-sql" data-lang="sql">(author=<span class="o">me()</span> OR author=test_user) AND created="19-08-2015" AND type=bug
</code></pre>


## Составные части

### Вспомогательные символы
* Скобочки <code>(</code> <code>)</code>
* Пробелы <code>&nbsp;</code> <code>\t</code> <code>\n</code>


## Лексер

{% highlight python %}
from funcparserlib.lexer import make_tokenizer, Token

SPECS = [
    ('CMP', (r'~=|>=|<=|@=|<|>|=',)),
    ('BR', (r'\(|\)',)),
    ('OP', (r'AND|OR',)),
    ('SPACE', (r'[ \t\r\n]+',)),
    ('STRING', (r'"(?:[^"\\]|\\.)*"',)),
    ('WORD', ('\w+',)),
]

tokenizer = make_tokenizer(SPECS)


def tokenize(query):
    return [tok for tok in tokenizer(query) if tok.type != 'SPACE']
{% endhighlight %}


## Токен

{% highlight python %}
class Token(object):
    def __init__(self, type, value, start=None, end=None):
        self.type = type
        self.value = value
        self.start = start
        self.end = end
{% endhighlight %}

## Проверяем
{% highlight python %}
In [3]: tokenize('author=zubchick AND title~=test OR created>=today()')
Out[3]:
[Token('WORD', 'author'),
 Token('CMP', '='),
 Token('WORD', 'zubchick'),
 Token('OP', 'AND'),
 Token('WORD', 'title'),
 Token('CMP', '~='),
 Token('WORD', 'test'),
 Token('OP', 'OR'),
 Token('WORD', 'created'),
 Token('CMP', '>='),
 Token('WORD', 'today'),
 Token('BR', '('),
 Token('BR', ')')]
{% endhighlight %}


## Пишем свой парсер
{:.section}

### Синтаксический анализ


## Грамматика

### Расширенная форма Бэкуса — Наура

{% highlight ebnf %}
expr       = orexpr;

orexpr     = andexpr, {"OR", andexpr};
andexpr    = basexpr, {"AND", basexpr};
basexpr    = "(" expr ")" | fieldexpr;

fieldexpr  = WORD, operator, (function | value);
operator   = "~=" | ">=" | "<=" | "@=" | "<" | ">" | "=";
function   = WORD, "(", ")";
value      = STRING | WORD;
{% endhighlight %}


## Теперь тоже самое на python

{% highlight python %}
from funcparserlib.parser import some, a, many, skip, forward_decl

# operator: '~=' | '>=' | '<=' | '<' | '>' | '=' | '@='
operator = some(lambda tok: tok.type == 'CMP')

string = some(lambda tok: tok.type == 'STRING')
word = some(lambda tok: tok.type == 'WORD')

OR = a(Token('OP', 'OR'))
AND = a(Token('OP', 'AND'))
{% endhighlight %}

## Field expression

{% highlight python %}
open_brace = skip(a(Token('BR', '(')))
close_brace = skip(a(Token('BR', ')')))
function = word + open_brace + close_brace

value = string | word
fieldexpr = word + operator + (function | value)
{% endhighlight %}


## Expression

{% highlight python %}
expr = forward_decl()

basexpr = open_brace + expr + close_brace | fieldexpr
andexpr = basexpr + many(AND + basexpr)
orexpr = andexpr + many(OR + andexpr)
expr.define(orexpr)
{% endhighlight %}


## Синтаксис
{% highlight sql %}
(author=me() OR author=test_user) AND created="19-08-2015" AND type=bug
{% endhighlight %}


## &nbsp;
{:.big-code}

{% highlight python %}
## Весь парсер на одном слайде

operator = some(lambda tok: tok.type == 'CMP')
string = some(lambda tok: tok.type == 'STRING')
word = some(lambda tok: tok.type == 'WORD')

OR = a(Token('OP', 'OR'))
AND = a(Token('OP', 'AND'))

open_brace = skip(a(Token('BR', '(')))
close_brace = skip(a(Token('BR', ')')))
function = word + open_brace + close_brace

value = string | word
fieldexpr = word + operator + (function | value)

expr = forward_decl()

basexpr = open_brace + expr + close_brace | fieldexpr
andexpr = basexpr + many(AND + basexpr)
orexpr = andexpr + many(OR + andexpr)
expr.define(orexpr)
{% endhighlight %}


## А вот что было
{% highlight ebnf %}
expr       = orexpr;

orexpr     = andexpr, {"OR", andexpr};
andexpr    = basexpr, {"AND", basexpr};
basexpr    = "(" expr ")" | fieldexpr;

fieldexpr  = WORD, operator, (function | value);
operator   = "~=" | ">=" | "<=" | "@=" | "<" | ">" | "=";
function   = WORD, "(", ")";
value      = STRING | WORD;
{% endhighlight %}


## Проверяем

{% highlight python %}
In [8]: expr.parse(tokenize(
            'author=zubchick AND title~=test AND created>=today()'
        ))
Out[8]:
(Token('WORD', 'author'),
 Token('CMP', '='),
 Token('WORD', 'zubchick'),
 [(Token('OP', 'AND'),
   (Token('WORD', 'title'), Token('CMP', '~='), Token('WORD', 'test'))),
  (Token('OP', 'AND'),
   (Token('WORD', 'created'), Token('CMP', '>='), Token('WORD', 'today')))],
 [])
{% endhighlight %}


## Синтаксический анализ
{:.section}

### AST

## &nbsp;
{:.big-code}
{% highlight python %}
class AST(object):
    children = ()


class Operator(AST):
    value = None

    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return "%s %s (%s)" % (self.__class__.__name__,
                               self.value, map(repr, self.children))


class LogicalOperator(Operator):
    pass


class CmpOperator(Operator):
    pass
{% endhighlight %}

## &nbsp;
{:.big-code}
{% highlight python %}
class Function(AST):
    def __init__(self, text):
        self.name = text.text

    def __repr__(self):
        return "%s()" % (self.name)


class Text(AST):
    def __init__(self, tok):
        self.text = tok.value

    def __repr__(self):
        return "Text(%s)" % self.text


class QuotedText(Text):
    def __init__(self, tok):
        self.text = tok.value[1:-1]

{% endhighlight %}


## &nbsp;
{:.big-code}
{% highlight python %}
class AndOp(LogicalOperator):
    value = 'AND'

class OrOp(LogicalOperator):
    value = 'OR'

class GtOp(CmpOperator):
    value = '>'

class LtOp(CmpOperator):
    value = '<'

class LteOp(CmpOperator):
    value = '<='

class GteOp(CmpOperator):
    value = '>='

class RegexOp(CmpOperator):
    value = '~='

class ContainsOp(CmpOperator):
    value = '@='
{% endhighlight %}



## Избавляемся от токенов
{% highlight python %}
operator = some(lambda tok: tok.type == 'CMP') >> choose_class

word = some(lambda tok: tok.type == 'WORD') >> Text
string = some(lambda tok: tok.type == 'STRING') >> Text

function = word + open_brace + close_brace >> Function

OR = a(Token('OP', 'OR')) >> lambda _: OrOp
AND = a(Token('OP', 'AND')) >> lambda _: AndOp
{% endhighlight %}


## Разворачиваем в дерево
{:.images .two}

<img width="400px" height="400px" src="pictures/ast1.svg">
*Результат работы парсера andexpr*

<img width="400px" height="400px" src="pictures/ast2.svg">
*AST*


## Разворачиваем в дерево
{% highlight python %}
def eval(data):
    arg1, lst = data
    for f, arg2 in lst:
        arg1 = f([arg1, arg2])

    return arg1
{% endhighlight %}

{% highlight python %}
def eval(data):
    lft, args = data
    return reduce(lambda arg1, (f, arg2): f([arg1, arg2]), args, lft)
{% endhighlight %}


## Eval
{% highlight python %}
andexpr = (basexpr + many(AND + basexpr)) >> eval
orexpr = (andexpr + many(OR + andexpr)) >> eval
{% endhighlight %}


## Проверяем
{% highlight sql %}
author=zubchick AND title~=test OR created>=today()
{% endhighlight %}

{% highlight bash %}
OrOp
|-- AndOp
|   |-- EqOp
|   |   |-- Text
|   |   `-- Text
|   `-- RegexOp
|       |-- Text
|       `-- Text
`-- GteOp
    |-- Text
    `-- Function
{% endhighlight %}


## AST
{:.section}

### Компиляция


## Компиляция запроса в монгу
{% highlight sql %}
author=zubchick AND title~=test OR created>=today()
{% endhighlight %}

{% highlight python %}
{'$or': [{'$and': [{'author': {'$eq': 'zubchick'}},
                   {'title': {'$regex': 'test'}}]},
         {'created': {'$gte': 1440761425}}]}
{% endhighlight %}


## &nbsp;
{:.big-code}
{% highlight python %}
class AndOp(LogicalOperator):
    value = 'AND'
    operator = '$and'

class OrOp(LogicalOperator):
    value = 'OR'
    operator = '$or'

class GtOp(CmpOperator):
    value = '>'
    operator = '$gt'

class RegexOp(CmpOperator):
    value = '~='
    operator = '$regex'

class ContainsOp(CmpOperator):
    value = '@='
    operator = '$in'

...
{% endhighlight %}


## &nbsp;
{:.big-code}
{% highlight python %}
class LogicalOperator(Operator):
    def compile(self):
        lft, right = self.children
        return {self.operator: [lft.compile(), right.compile()]}


class CmpOperator(Operator):
    def compile(self):
        lft, right = self.children
        return {left.compile(): {self.operator: right.compile()}}

class Function(AST):
    func_map = {
        'me': os.getlogin,
        'today': lambda: int(datetime.today().strftime('%s')),
    }

    def compile():
        return self.func_map[self.name]()


class Text(AST):
    def compile(self):
        return self.text
{% endhighlight %}


## &nbsp;
{:.big-code}
{% highlight bash %}
Original query:
author=zubchick AND title~=test OR created>=today()

AST:
OrOp
|-- AndOp
|   |-- EqOp
|   |   |-- Text
|   |   `-- Text
|   `-- RegexpOp
|       |-- Text
|       `-- Text
`-- LteOp
    |-- Text
    `-- Function

Mongo request:
{'$or': [{'$and': [{'author': {'$eq': 'zubchick'}},
                   {'title': {'$regex': 'test'}}]},
         {'created': {'$gte': 1440761756}}]}
{% endhighlight %}

## &nbsp;
{:.big-code}
{% highlight bash %}
Original query:
(author=me() OR author=test_user) AND created="19-08-2015" AND type=bug

AST:
AndOp
|-- AndOp
|   |-- OrOp
|   |   |-- EqOp
|   |   |   |-- Text
|   |   |   `-- Function
|   |   `-- EqOp
|   |       |-- Text
|   |       `-- Text
|   `-- EqOp
|       |-- Text
|       `-- QuotedText
`-- EqOp
    |-- Text
    `-- Text

Mongo request:
{'$and': [{'$and': [{'$or': [{'author': {'$eq': 'zubchick'}},
                             {'author': {'$eq': 'test_user'}}]},
                    {'created': {'$eq': '19-08-2015'}}]},
          {'type': {'$eq': 'bug'}}]}
{% endhighlight %}

## Что можно улучшить
* Добавить операторов
* Добавить функций
* Прокидывать контекст в функцию compile
* Добавить проверку прав
* Оптимизировать дерево
* Генерировать sql после переезда на postrgresql

## **Контакты** {#contacts}

<div class="info">
<p class="author">{{ site.author.name }}</p>
<p class="position">{{ site.author.position }}</p>

    <div class="contacts">
        <p class="contacts-left mail">zubchick@yandex-team.ru</p>
        <p class="contacts-left contacts-top twitter">@zubchick</p>

    </div>
</div>
