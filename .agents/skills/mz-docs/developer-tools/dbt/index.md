# Use dbt to manage Materialize

How to use dbt and Materialize to transform streaming data in real time.

[dbt](https://docs.getdbt.com/docs/introduction) has become the standard for
data transformation ("the T in ELT"). It combines the accessibility of SQL with
software engineering best practices, allowing you to not only build reliable
data pipelines, but also document, test and version-control them.

Setting up a dbt project with Materialize is similar to setting it up with any
other database that requires a non-native adapter.

> **Note:** The `dbt-materialize` adapter can only be used with **dbt Core**. Making the
> adapter available in dbt Cloud depends on prioritization by dbt Labs. If you
> require dbt Cloud support, please [reach out to the dbt Labs team](https://www.getdbt.com/community/join-the-community/).

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="./get-started/" >Get started with dbt and Materialize</a>
</div>

<div class="linkbox ">
  <div class="title">
    Development guidelines
  </div>
  <a href="./development-workflows" >Development guidelines</a>
</div>

<div class="linkbox ">
  <div class="title">
    Deployment
  </div>
  <ul>
<li>
<p><a href="/developer-tools/dbt/blue-green-deployments/" >Blue-green deployment guide</a></p>
</li>
<li>
<p><a href="/developer-tools/dbt/slim-deployments/" >Slim deployment guide</a></p>
</li>
</ul>

</div>

</div>

## See also

As a tool primarily meant to manage your data model, the `dbt-materialize`
adapter does not expose all Materialize objects types. If there is a **clear
separation** between data modeling and **infrastructure management ownership**
in your team, and you want to manage objects like
[clusters](/fundamentals/concepts/clusters/), [connections](/sql/create-connection/), or
[secrets](/sql/create-secret/) as code, we recommend using the [Materialize
Terraform provider](/developer-tools/terraform/) as a complementary deployment tool.

## Pages in this section

- [Blue-green deployment](/developer-tools/dbt/blue-green-deployments/index.md): How to use dbt for blue-green deployments.
- [Development guidelines](/developer-tools/dbt/development-workflows/index.md): How to use dbt to develop and test changes to your SQL code against Materialize.
- [Get started with dbt and Materialize](/developer-tools/dbt/get-started/index.md): How to use dbt and Materialize to transform streaming data in real time.
- [Slim deployments](/developer-tools/dbt/slim-deployments/index.md): How to use dbt for slim deployments.
