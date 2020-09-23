from dataclasses import dataclass
from injector import inject

from model.enforcement import Enforcement
from helper.logger import logger


from argocd_client import V1alpha1ApplicationDestination, V1alpha1Application, V1alpha1ApplicationSpec, \
    ApplicationServiceApi, V1ObjectMeta, V1alpha1SyncPolicy, V1alpha1SyncPolicyAutomated


@inject
@dataclass
class EnforcementRepository:
    _application_service: ApplicationServiceApi

    def create_enforcement(self, enforcement: Enforcement):

        application = V1alpha1Application(
            metadata=V1ObjectMeta(
               name=enforcement.name
            ),
            spec=V1alpha1ApplicationSpec(
                destination=V1alpha1ApplicationDestination(
                    name=enforcement.cluster_name
                ),
                source=enforcement.render(),
                sync_policy=V1alpha1SyncPolicy(
                    automated=V1alpha1SyncPolicyAutomated(
                        prune=True,
                        self_heal=True,
                    )
                )
            )
        )

        self._application_service.create_mixin9(application)
        logger.info(f"Application {application.metadata.name} created")



    def remove_enforcement(self, enforcement: Enforcement):

        application = V1alpha1Application(
            metadata=V1ObjectMeta(
               name=enforcement.name
            )
        )

        self._application_service.delete_mixin9(application.metadata.name)
        logger.info(f"Application {application.metadata.name} removed")

