module Esi::Errors
  class NotFound < Base

    def pause
      sleep 60
    end

    def retry?
      true
    end

  end
end
