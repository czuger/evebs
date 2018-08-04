FactoryBot.define do
  factory :user do

    # Important for OmniauthTests
    provider :developer

    sequence :name do |n|
      "User #{n}"
    end

    remove_occuped_places true
    min_pcent_for_advice 10
    min_amount_for_advice 10000000

    uid 12345677

    # identity
    #
    # transient do
    #   region nil
    # end
    #
    # after(:create) do |user, evaluator|
    #   user.eve_items = EveItem.all
    #   user.trade_hubs = evaluator.region.trade_hubs if evaluator.region
    # end

  end
end
