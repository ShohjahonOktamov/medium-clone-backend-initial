from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from .serializers import ArticleListSerializer, ArticleDetailSerializer

articles_list_response: OpenApiResponse = \
    OpenApiResponse(description="OK", response=ArticleListSerializer(many=True),
                    examples=[
                        OpenApiExample(name="Articles List",
                                       description="List of Articles Details",
                                       value={
                                           'application/json':
                                               {
                                                   "count": 1,
                                                   "next": None,
                                                   "previous": None,
                                                   "results": [
                                                       {
                                                           "id": 1,
                                                           "author": {
                                                               "id": 1,
                                                               "username": "user",
                                                               "first_name": "John",
                                                               "last_name": "Doe",
                                                               "middle_name": "Johnson",
                                                               "email": "johndoe123@mail.com",
                                                               "avatar": None
                                                           },
                                                           "title": "Python",
                                                           "summary": "This article is about Python",
                                                           "content": "<p>Python is a programming language</p>",
                                                           "status": "publish",
                                                           "thumbnail": None,
                                                           "views_count": 60,
                                                           "reads_count": 30,
                                                           "topics": [
                                                               {
                                                                   "id": 1,
                                                                   "name": "Programming",
                                                                   "description": "This topic is about programming",
                                                                   "is_active": True
                                                               }
                                                           ],
                                                           "created_at": "2024-08-27 14:45:14",
                                                           "updated_at": "2024-08-27 14:45:14",
                                                           "claps_count": 25,
                                                           "comments_count": 10
                                                       }
                                                   ]
                                               }
                                       }
                                       )
                    ]
                    )

unauthorized_response: OpenApiResponse = \
    OpenApiResponse(description="Unauthorized",
                    examples=[
                        OpenApiExample(name="No Authorization Token",
                                       description="Response With No Authorization Token",
                                       value=
                                       {'application/json': {
                                           'detail': "Authentication credentials were not provided."
                                       }
                                       }
                                       )
                    ],
                    )

article_detail_response: OpenApiResponse = \
    OpenApiResponse(description="OK", response=ArticleDetailSerializer,
                    examples=[OpenApiExample(name="Article Details",
                                             description="Single Article Details",
                                             value={
                                                 'application/json': {
                                                     "id": 1,
                                                     "author": {
                                                         "id": 1,
                                                         "username": "user",
                                                         "first_name": "John",
                                                         "last_name": "Doe",
                                                         "middle_name": "Johnson",
                                                         "email": "johndoe123@mail.com",
                                                         "avatar": None
                                                     },
                                                     "title": "Python",
                                                     "summary": "This article is about Python",
                                                     "content": "<p>Python is a programming language</p>",
                                                     "status": "publish",
                                                     "thumbnail": None,
                                                     "views_count": 60,
                                                     "reads_count": 30,
                                                     "topics": [
                                                         {
                                                             "id": 1,
                                                             "name": "Programming",
                                                             "description": "This topic is about programming",
                                                             "is_active": True
                                                         }
                                                     ],
                                                     "created_at": "2024-08-27 14:45:14",
                                                     "updated_at": "2024-08-27 14:45:14",
                                                     "claps_count": 25,
                                                     "comments_count": 10
                                                 }

                                             }
                                             )
                              ]
                    )

no_article_matches_response: OpenApiResponse = \
    OpenApiResponse(description="Not Found", examples=[
        OpenApiExample(name="Article Not Found", description="No Article matches the given query", value={
            'application/json': {
                'detail': "No Article matches the given query."
            }
        }
                       )
    ]
                    )

bad_request_response: OpenApiResponse = \
    OpenApiResponse(description="Bad Request")

no_content_response: OpenApiResponse = \
    OpenApiResponse(description="No Content",
                    examples=[OpenApiExample(name="No Content", description="Nothing To Return", value={
                        'application/json': {

                        }
                    }
                                             )
                              ]
                    )

forbidden_response: OpenApiResponse = \
    OpenApiResponse(description="Forbidden", examples=[
        OpenApiExample(name="Forbidden", description="User does not have permission to perform the cation", value={
            'application/json': {
                'detail': "You do not have permission to perform this action."
            }
        }
                       )
    ]
                    )

article_read_response: OpenApiResponse = \
    OpenApiResponse(description="Created", examples=[
        OpenApiExample(name="Article Read", description="Article Reads Count was successfully incremented", value={
            "detail": "Maqolani o'qish soni ortdi."
        }
                       )
    ]
                    )

article_archived: OpenApiResponse = \
    OpenApiResponse(description="OK", examples=[
        OpenApiExample(name="Article Archived", description="Article was Successfully Archived",
                       value={"detail": "Maqola arxivlandi."
                              }
                       )
    ]
                    )

article_pin: OpenApiResponse = \
    OpenApiResponse(description="OK", examples=[
        OpenApiExample(name="Article Pinned", description="Article was successfully Pinned",
                       value={"detail": "Maqola pin qilindi."}
                       )
    ]
                    )

article_already_pinned = \
    OpenApiResponse(description="Bad Request", examples=[
        OpenApiExample(name="Article Already Pinned", description="Article Is Already Pinned", value={
            "detail": "Maqola allaqachon pin qilingan."
        })])

article_not_found = \
    OpenApiResponse(description="Not Found",
                    examples=[OpenApiExample(name="Article Not Found", description="Article or Pin not found", value={
                        'application/json': {
                            'detail': "Maqola topilmadi.."
                        }
                    })])
