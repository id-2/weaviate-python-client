from typing import (
    Generic,
    List,
    Optional,
    Type,
    Union,
    cast,
    get_type_hints,
)

from weaviate.collection.classes.config import ConsistencyLevel

from weaviate.collection.classes.filters import _Filters
from weaviate.collection.classes.grpc import (
    HybridFusion,
    MetadataQuery,
    Move,
    PROPERTIES,
)
from weaviate.collection.classes.internal import _Object
from weaviate.collection.classes.orm import Model

from weaviate.collection.grpc.base.query import SearchResult
from weaviate.collection.grpc.queries.bm25 import _BM25
from weaviate.collection.grpc.queries.get import _Get
from weaviate.collection.grpc.queries.hybrid import _Hybrid
from weaviate.collection.grpc.queries.near_audio import _NearAudio
from weaviate.collection.grpc.queries.near_image import _NearImage
from weaviate.collection.grpc.queries.near_object import _NearObject
from weaviate.collection.grpc.queries.near_text import _NearText
from weaviate.collection.grpc.queries.near_vector import _NearVector
from weaviate.collection.grpc.queries.near_video import _NearVideo
from weaviate.collection.grpc.base.wrapper import _Grpc

from weaviate.connect import Connection
from weaviate.weaviate_types import UUID
from weaviate_grpc import weaviate_pb2


class _GrpcCollection(
    _BM25,
    _Get,
    _Hybrid,
    _NearAudio,
    _NearImage,
    _NearObject,
    _NearText,
    _NearVector,
    _NearVideo,
):
    pass


class _GrpcCollectionModel(Generic[Model], _Grpc):
    def __init__(
        self,
        connection: Connection,
        name: str,
        model: Type[Model],
        tenant: Optional[str] = None,
        consistency_level: Optional[ConsistencyLevel] = None,
    ):
        super().__init__(connection, name, consistency_level, tenant)
        self.model = model

    def __parse_result(
        self,
        properties: "weaviate_pb2.ResultProperties",
        type_: Type[Model],
    ) -> Model:
        hints = get_type_hints(type_)

        result = {}

        for name, non_ref_prop in properties.non_ref_properties.items():
            result[name] = self._deserialize_primitive(non_ref_prop, hints.get(name))

        for ref_prop in properties.ref_props:
            hint = hints.get(ref_prop.prop_name)
            if hint is not None:
                referenced_property_type = (lambda: "TODO: implement this")()
                result[ref_prop.prop_name] = [
                    _Object(
                        properties=self.__parse_result(
                            prop, cast(Type[Model], referenced_property_type)
                        ),
                        metadata=self._extract_metadata_for_object(prop.metadata),
                    )
                    for prop in ref_prop.properties
                ]
            else:
                raise ValueError(
                    f"Property {ref_prop.prop_name} is not defined with a Reference[Model] type hint in the model {self.model}"
                )

        return type_(**result)

    def __result_to_object(self, res: SearchResult) -> _Object[Model]:
        properties = self.__parse_result(res.properties, self.model)
        metadata = self._extract_metadata_for_object(res.additional_properties)
        return _Object[Model](properties=properties, metadata=metadata)

    def get(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .get(
                limit=limit,
                offset=offset,
                after=after,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def hybrid(
        self,
        query: str,
        alpha: Optional[float] = None,
        vector: Optional[List[float]] = None,
        query_properties: Optional[List[str]] = None,
        fusion_type: Optional[HybridFusion] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .hybrid(
                query=query,
                alpha=alpha,
                vector=vector,
                properties=query_properties,
                fusion_type=fusion_type,
                limit=limit,
                autocut=auto_limit,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def bm25(
        self,
        query: str,
        query_properties: Optional[List[str]] = None,
        limit: Optional[int] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .bm25(
                query=query,
                properties=query_properties,
                limit=limit,
                autocut=auto_limit,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_vector(
        self,
        near_vector: List[float],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_vector(
                near_vector=near_vector,
                certainty=certainty,
                distance=distance,
                autocut=auto_limit,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_object(
        self,
        near_object: UUID,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_object(
                near_object=near_object,
                certainty=certainty,
                distance=distance,
                autocut=auto_limit,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_text(
        self,
        query: Union[List[str], str],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        move_to: Optional[Move] = None,
        move_away: Optional[Move] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_text(
                near_text=query,
                certainty=certainty,
                distance=distance,
                move_to=move_to,
                move_away=move_away,
                autocut=auto_limit,
                filters=filters,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_image(
        self,
        near_image: str,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_image(
                image=near_image,
                certainty=certainty,
                distance=distance,
                filters=filters,
                autocut=auto_limit,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_audio(
        self,
        near_audio: str,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_audio(
                audio=near_audio,
                certainty=certainty,
                distance=distance,
                filters=filters,
                autocut=auto_limit,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]

    def near_video(
        self,
        near_video: str,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        auto_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        return_metadata: Optional[MetadataQuery] = None,
        return_properties: Optional[PROPERTIES] = None,
    ) -> List[_Object[Model]]:
        return [
            self.__result_to_object(obj)
            for obj in self._query()
            .near_video(
                video=near_video,
                certainty=certainty,
                distance=distance,
                filters=filters,
                autocut=auto_limit,
                return_metadata=return_metadata,
                return_properties=return_properties,
            )
            .results
        ]
