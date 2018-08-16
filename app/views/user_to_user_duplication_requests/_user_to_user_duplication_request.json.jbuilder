json.extract! user_to_user_duplication_request, :id, :reciever_id, :duplication_type, :created_at, :updated_at
json.url user_to_user_duplication_request_url(user_to_user_duplication_request, format: :json)
