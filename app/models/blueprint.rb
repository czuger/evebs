class Blueprint < ActiveRecord::Base
  belongs_to :eve_item
  has_many :materials
  validates :eve_item_id, :nb_runs, :prod_qtt, :cpp_blueprint_id, presence: true
end
