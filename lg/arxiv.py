import arxiv

# def get_daily_papers(topic,query="slam", max_results=2):
#     """
#     @param topic: str
#     @param query: str
#     @return paper_with_code: dict
#     """

#     # output
#     content = dict()
#     content_to_web = dict()

#     # content
#     output = dict()

#     search_engine = arxiv.Search(
#         query = query,
#         max_results = max_results,
#         sort_by = arxiv.SortCriterion.SubmittedDate
#     )

#     cnt = 0

#     for result in search_engine.results():

#         paper_id            = result.get_short_id()
#         paper_title         = result.title
#         paper_url           = result.entry_id
#         code_url            = base_url + paper_id
#         paper_abstract      = result.summary.replace("\n"," ")
#         paper_authors       = get_authors(result.authors)
#         paper_first_author  = get_authors(result.authors,first_author = True)
#         primary_category    = result.primary_category
#         publish_time        = result.published.date()
#         update_time         = result.updated.date()
#         comments            = result.comment


#         print("Time = ", update_time ,
#               " title = ", paper_title,
#               " author = ", paper_first_author)

#         # eg: 2108.09112v1 -> 2108.09112
#         ver_pos = paper_id.find('v')
#         if ver_pos == -1:
#             paper_key = paper_id
#         else:
#             paper_key = paper_id[0:ver_pos]

#         try:
#             r = requests.get(code_url).json()
#             # source code link
#             if "official" in r and r["official"]:
#                 cnt += 1
#                 repo_url = r["official"]["url"]
#                 content[paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|**[link]({repo_url})**|\n"
#                 content_to_web[paper_key] = f"- {update_time}, **{paper_title}**, {paper_first_author} et.al., Paper: [{paper_url}]({paper_url}), Code: **[{repo_url}]({repo_url})**"

#             else:
#                 content[paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|null|\n"
#                 content_to_web[paper_key] = f"- {update_time}, **{paper_title}**, {paper_first_author} et.al., Paper: [{paper_url}]({paper_url})"

#             # TODO: select useful comments
#             comments = None
#             if comments != None:
#                 content_to_web[paper_key] = content_to_web[paper_key] + f", {comments}\n"
#             else:
#                 content_to_web[paper_key] = content_to_web[paper_key] + f"\n"

#         except Exception as e:
#             print(f"exception: {e} with id: {paper_key}")

#     data = {topic:content}
#     data_web = {topic:content_to_web}
#     return data,data_web

# Initialize the library
search = arxiv.Search(
    query="cat:cs.AI",
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending,
)

# Fetch the new submissions
new_submissions = search.results()

# Print the titles and links
for result in new_submissions:
    print(f"Title: {result.title}")
    print(f"Link: https://arxiv.org/abs/{result.entry_id}")
    print(f"Abstract: {result.summary}")
