class User < ActiveRecord::Base
  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs

  has_many :blueprints, through: :eve_items
  has_many :materials, through: :blueprints
  has_many :components, through: :materials
end
