FactoryBot.define do
  factory :user_to_user_duplication_request do
    sender 1
    reciever 1
    duplication_type "MyString"
  end
end
