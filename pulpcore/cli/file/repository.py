from typing import Optional

import click

from pulpcore.cli.common import limit_option, offset_option, PulpContext, PulpEntityContext
from pulpcore.cli.file.remote import PulpFileRemoteContext


class PulpFileRepositoryContext(PulpEntityContext):
    ENTITY: str = "repository"
    HREF: str = "file_file_repository_href"
    LIST_ID: str = "repositories_file_file_list"
    CREATE_ID: str = "repositories_file_file_create"
    UPDATE_ID: str = "repositories_file_file_update"
    DELETE_ID: str = "repositories_file_file_delete"
    SYNC_ID: str = "repositories_file_file_sync"


@click.group()
@click.option(
    "-t",
    "--type",
    "repo_type",
    type=click.Choice(["file"], case_sensitive=False),
    default="file",
)
@click.pass_context
def repository(ctx: click.Context, repo_type: str) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)

    if repo_type == "file":
        ctx.obj = PulpFileRepositoryContext(pulp_ctx)
    else:
        raise NotImplementedError()


@repository.command()
@limit_option
@offset_option
@click.pass_context
def list(ctx: click.Context, limit: int, offset: int) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    repository_ctx: PulpFileRepositoryContext = ctx.find_object(PulpFileRepositoryContext)

    result = repository_ctx.list(limit=limit, offset=offset, parameters={})
    pulp_ctx.output_result(result)


@repository.command()
@click.option("--name", required=True)
@click.option("--description")
@click.option("--remote")
@click.pass_context
def create(
    ctx: click.Context, name: str, description: Optional[str], remote: Optional[str]
) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    repository_ctx: PulpFileRepositoryContext = ctx.find_object(PulpFileRepositoryContext)

    repository = {"name": name, "description": description}
    if remote:
        remote_href: str = PulpFileRemoteContext(pulp_ctx).find(name=remote)["pulp_href"]
        repository["remote"] = remote_href

    result = repository_ctx.create(body=repository)
    pulp_ctx.output_result(result)


@repository.command()
@click.option("--name", required=True)
@click.option("--description")
@click.option("--remote")
@click.pass_context
def update(
    ctx: click.Context, name: str, description: Optional[str], remote: Optional[str]
) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    repository_ctx: PulpFileRepositoryContext = ctx.find_object(PulpFileRepositoryContext)

    repository = repository_ctx.find(name=name)
    repository_href = repository["pulp_href"]

    if description is not None:
        if description == "":
            # unset the description
            description = None
        if description != repository["description"]:
            repository["description"] = description

    if remote is not None:
        if remote == "":
            # unset the remote
            repository["remote"] = ""
        elif remote:
            remote_href: str = PulpFileRemoteContext(pulp_ctx).find(name=remote)["pulp_href"]
            repository["remote"] = remote_href

    repository_ctx.update(repository_href, body=repository)


@repository.command()
@click.option("--name", required=True)
@click.pass_context
def destroy(ctx: click.Context, name: str) -> None:
    repository_ctx: PulpFileRepositoryContext = ctx.find_object(PulpFileRepositoryContext)

    repository = repository_ctx.find(name=name)
    repository_href = repository["pulp_href"]
    repository_ctx.delete(repository_href)


@repository.command()
@click.option("--name", required=True)
@click.option("--remote")
@click.option("-b", "--background", is_flag=True)
@click.pass_context
def sync(ctx: click.Context, name: str, remote: Optional[str], background: bool) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    repository_ctx: PulpFileRepositoryContext = ctx.find_object(PulpFileRepositoryContext)

    repository = repository_ctx.find(name=name)
    repository_href = repository["pulp_href"]

    body = {}

    if remote:
        remote_href: str = PulpFileRemoteContext(pulp_ctx).find(name=remote)["pulp_href"]
        body["remote"] = remote_href
    elif repository["remote"] is None:
        raise click.ClickException(
            f"Repository '{name}' does not have a default remote. Please specify with '--remote'."
        )

    pulp_ctx.call(
        repository_ctx.SYNC_ID,
        parameters={repository_ctx.HREF: repository_href},
        background=background,
        body=body,
    )