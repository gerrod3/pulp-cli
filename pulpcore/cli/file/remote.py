import click

from pulpcore.cli.common import limit_option, offset_option, PulpContext, PulpEntityContext


class PulpFileRemoteContext(PulpEntityContext):
    ENTITY: str = "remote"
    HREF: str = "file_file_remote_href"
    LIST_ID: str = "remotes_file_file_list"
    CREATE_ID: str = "remotes_file_file_create"
    UPDATE_ID: str = "remotes_file_file_update"
    DELETE_ID: str = "remotes_file_file_delete"


@click.group()
@click.option(
    "-t",
    "--type",
    "remote_type",
    type=click.Choice(["file"], case_sensitive=False),
    default="file",
)
@click.pass_context
def remote(ctx: click.Context, remote_type: str) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)

    if remote_type == "file":
        ctx.obj = PulpFileRemoteContext(pulp_ctx)
    else:
        raise NotImplementedError()


@remote.command()
@limit_option
@offset_option
@click.pass_context
def list(ctx: click.Context, limit: int, offset: int) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    remote_ctx: PulpFileRemoteContext = ctx.find_object(PulpFileRemoteContext)

    result = remote_ctx.list(limit=limit, offset=offset, parameters={})
    pulp_ctx.output_result(result)


@remote.command()
@click.option("--name", required=True)
@click.option("--url", required=True)
@click.pass_context
def create(ctx: click.Context, name: str, url: str) -> None:
    pulp_ctx: PulpContext = ctx.find_object(PulpContext)
    remote_ctx: PulpFileRemoteContext = ctx.find_object(PulpFileRemoteContext)

    remote = {"name": name, "url": url}
    result = remote_ctx.create(body=remote)
    pulp_ctx.output_result(result)


@remote.command()
@click.option("--name", required=True)
@click.pass_context
def destroy(ctx: click.Context, name: str) -> None:
    remote_ctx: PulpFileRemoteContext = ctx.find_object(PulpFileRemoteContext)

    remote = remote_ctx.find(name=name)
    remote_href: str = remote["pulp_href"]
    remote_ctx.delete(remote_href)