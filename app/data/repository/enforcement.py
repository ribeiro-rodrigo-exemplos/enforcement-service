from dataclasses import dataclass
from typing import Dict, List, Any

from injector import inject
from argocd_client import (
    V1alpha1ApplicationDestination,
    V1alpha1Application,
    V1alpha1ApplicationSpec,
    ApplicationServiceApi,
    V1ObjectMeta,
    V1alpha1SyncPolicy,
    V1alpha1SyncPolicyAutomated,
    V1alpha1ApplicationList,
    V1alpha1ApplicationSource,
    V1alpha1ApplicationSourceHelm,
    V1alpha1HelmParameter
)

from app.model.entities import Enforcement, Helm
from app.helper.logger import logger


@inject
@dataclass
class EnforcementRepository:
    _application_service: ApplicationServiceApi

    def create_enforcement(self, cluster_name: str, enforcement: Enforcement) -> None:
        application = self._make_application_by_enforcement(cluster_name, enforcement)
        self._application_service.create_mixin9(application)

    def update_enforcement(self, cluster_name: str, enforcement: Enforcement) -> None:
        application = self._make_application_by_enforcement(cluster_name, enforcement)
        self._application_service.update_mixin9(application.metadata.name, application)

    def remove_enforcement(self, enforcement: Enforcement) -> None:
        application = V1alpha1Application(
            metadata=V1ObjectMeta(
               name=enforcement.name
            )
        )

        self._application_service.delete_mixin9(application.metadata.name, cascade=False)
        logger.info(f"Application {application.metadata.name} removed")

    def list_installed_enforcements(self, **filters: Any) -> List[Enforcement]:
        labels = self._make_labels(filters)
        application_list: V1alpha1ApplicationList = self._application_service.list_mixin9(
            selector=labels
        )

        applications: List[V1alpha1Application] = application_list.items if application_list.items else []

        enforcements = [
            self._make_enforcement_by_application(application)
            for application in applications
        ]

        return enforcements

    def _make_labels(self, labels: Dict[str, str]) -> str:
        list_labels = [f"{key}={value}" for key, value in list(labels.items())]
        separator = ","
        return separator.join(list_labels)

    def _make_application_by_enforcement(self, cluster_name: str, enforcement: Enforcement) -> V1alpha1Application:
        source = V1alpha1ApplicationSource(path=enforcement.path, repo_url=enforcement.repo)

        if enforcement.helm:
            source.helm = V1alpha1ApplicationSourceHelm(
                    parameters=[
                        V1alpha1HelmParameter(
                            name=key,
                            value=value
                        )
                        for key, value in enforcement.helm.parameters.items()
                    ] if enforcement.helm.parameters else []
            )

        return V1alpha1Application(
            metadata=V1ObjectMeta(
               name=f"{cluster_name}-{enforcement.name}",
               labels={"cluster_name": cluster_name, "enforcement_name": enforcement.name},
            ),
            spec=V1alpha1ApplicationSpec(
                destination=V1alpha1ApplicationDestination(
                    name=cluster_name,
                    namespace=enforcement.namespace
                ),
                source=source,
                sync_policy=V1alpha1SyncPolicy(
                    automated=V1alpha1SyncPolicyAutomated(
                        prune=False,
                        self_heal=True,
                    )
                )
            )
        )

    def _make_enforcement_by_application(self, application: V1alpha1Application) -> Enforcement:

        helm_source: V1alpha1ApplicationSourceHelm = application.spec.source.helm
        helm = None

        if helm_source and helm_source.parameters:
            helm_params = {param.name: param.value for param in helm_source.parameters}
            helm = Helm(parameters=helm_params)

        return Enforcement(
            name=application.metadata.labels["enforcement_name"],
            repo=application.spec.source.repo_url,
            path=application.spec.source.path,
            helm=helm
        )