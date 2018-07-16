class Character < ApplicationRecord
  belongs_to :user

  has_many :bpc_assets

  has_many :production_list_share_requests, foreign_key: :recipient_id

  has_one :character_pl_share, class_name: 'Character', primary_key: :character_pl_share_id, foreign_key: :id
end
