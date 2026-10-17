# Use Terraform to manage Materialize

Create and manage Materialize resources with Terraform

[Terraform](https://www.terraform.io/) is an infrastructure-as-code tool that
allows you to manage your resources in a declarative configuration language.
Materialize maintains a [Terraform provider](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs)
to help you safely and predictably provision and manage connections, sources,
and other database objects.

Materialize also maintains [several
modules](/developer-tools/terraform/manage-cloud-modules) that make it easier to manage
other cloud resources that Materialize depends on. Modules allow you to bypass
manually configuring cloud resources and are an efficient way of deploying
infrastructure with a single `terraform apply` command.

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="./get-started/" >Get started with Terraform and Materialize</a>
</div>

<div class="linkbox ">
  <div class="title">
    Manage resources
  </div>
  <p><a href="./manage-resources" >Manage Materialize resources</a></p>
<p><a href="./manage-cloud-modules/" >Manage cloud resources</a></p>

</div>

<div class="linkbox ">
  <div class="title">
    Additional modules
  </div>
  <ul>
<li><a href="./appendix-secret-stores/" >Appendix: Secret stores</a></li>
</ul>

</div>

</div>

## Contributing

If you want to help develop the Materialize provider, check out the [contribution guidelines](https://github.com/MaterializeInc/terraform-provider-materialize/blob/main/CONTRIBUTING.md).

## Pages in this section

- [Appendix: External secret stores](/developer-tools/terraform/appendix-secret-stores/index.md)
- [Get started with the Materialize provider](/developer-tools/terraform/get-started/index.md): Introductory setup with Materialize Terraform provider
- [Manage cloud resources](/developer-tools/terraform/manage-cloud-modules/index.md): Use Terraform modules to set up cloud resources
- [Manage Materialize resources with the Materialize provider](/developer-tools/terraform/manage-resources/index.md)
- [Manage privileges](/developer-tools/terraform/manage-rbac/index.md): Add users, create roles, and assign privileges in Materialize with Terraform
