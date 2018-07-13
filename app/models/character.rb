class Character < ApplicationRecord
  belongs_to :user

  has_many :bpc_assets
end
