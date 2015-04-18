json.array!(@users) do |user|
  json.extract! user, :id, :edit, :name, :remove_occuped_places, :key_user_id, :api_key
  json.url user_url(user, format: :json)
end
