class Blueprint < ApplicationRecord

  TAX_AMOUNT= 0.03
  TAX_AMOUNT_MULTIPLIER = TAX_AMOUNT+1

  belongs_to :eve_item, dependent: :destroy
  has_many :blueprint_materials, dependent: :destroy

  def batch_elements_count
    prod_qtt*nb_runs
  end

end