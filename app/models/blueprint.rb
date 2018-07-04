class Blueprint < ApplicationRecord

  TAX_AMOUNT= 0.11

  belongs_to :eve_item, dependent: :destroy
  has_many :blueprint_materials, dependent: :destroy

  def batch_elements_count
    prod_qtt*nb_runs
  end

end