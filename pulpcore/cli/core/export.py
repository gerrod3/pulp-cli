import gettext
from typing import Any, Dict, List, Optional

import click

from pulpcore.cli.common.context import (
    DEFAULT_LIMIT,
    PulpContext,
    RepositoryVersionDefinition,
    pass_entity_context,
    pass_pulp_context,
)
from pulpcore.cli.common.generic import create_command, list_command, destroy_command, href_option, show_command
from pulpcore.cli.core.context import PulpExportContext, PulpExporterContext

_ = gettext.gettext


def _exporter_callback(ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    if value is not None:
        export_ctx: PulpExportContext = ctx.find_object(PulpExportContext)
        exporter_ctx = PulpExporterContext(export_ctx.pulp_ctx)
        export_ctx.exporter = exporter_ctx.find(name=value)
    return value


@click.group()
def export() -> None:
    pass


@export.group()
@pass_pulp_context
@click.pass_context
def pulp(ctx: click.Context, pulp_ctx: PulpContext) -> None:
    ctx.obj = PulpExportContext(pulp_ctx)


lookup_options = [href_option]
exporter_option = click.option(
    "--exporter",
    type=str,
    required=True,
    help=_("Name of owning PulpExport"),
    callback=_exporter_callback,
    expose_value=False
)

pulp.add_command(list_command(decorators=[exporter_option]))
pulp.add_command(show_command(decorators=lookup_options))
pulp.add_command(destroy_command(decorators=lookup_options))


@pulp.command(deprecated=True)
@click.option("--href", required=True, help=_("HREF of the PulpExport"))
@pass_entity_context
@pass_pulp_context
def read(pulp_ctx: PulpContext, export_ctx: PulpExportContext, href: str) -> None:
    """Shows details of an artifact."""
    entity = export_ctx.show(href)
    pulp_ctx.output_result(entity)


@pulp.command(deprecated=True)
@click.option("--href", required=True)
@pass_entity_context
@pass_pulp_context
def delete(pulp_ctx: PulpContext, export_ctx: PulpExportContext, href: str) -> None:
    result = export_ctx.delete(href)
    pulp_ctx.output_result(result)



@pulp.command()
@click.option("--exporter", required=True)
@click.option("--full", type=bool, default=True)
@click.option("--chunk-size", type=str, help=_("Examples: 512MB, 1GB"))
@click.option("--versions", type=tuple([str, str, int]), multiple=True)
@click.option("--start-versions", type=tuple([str, str, int]), multiple=True)
@pass_entity_context
@pass_pulp_context
def run(
    pulp_ctx: PulpContext,
    export_ctx: PulpExportContext,
    exporter: str,
    full: bool,
    chunk_size: str,
    versions: List[RepositoryVersionDefinition],
    start_versions: List[RepositoryVersionDefinition],
) -> None:
    exporter_ctx = PulpExporterContext(pulp_ctx)
    export_ctx.exporter = exporter_ctx.find(name=exporter)

    body: Dict[str, Any] = dict(full=full)

    if chunk_size:
        body["chunk_size"] = chunk_size

    vers_list = []
    for v in versions:
        vers_list.append(export_ctx.find_repository_version(v)["pulp_href"])
    if vers_list:
        body["versions"] = vers_list

    start_vers_list = []
    for v in start_versions:
        start_vers_list.append(export_ctx.find_repository_version(v)["pulp_href"])
    if start_vers_list:
        body["start_versions"] = start_vers_list

    result = export_ctx.create(body=body)
    pulp_ctx.output_result(result)
