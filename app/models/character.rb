class Character < ApplicationRecord
  belongs_to :user

  has_many :bpc_assets

  has_many :production_list_share_requests, foreign_key: :recipient_id
end
