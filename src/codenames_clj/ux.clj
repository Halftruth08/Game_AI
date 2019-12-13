(ns codenames_clj.ux
 (:require [clojure.java.io :as io]
           [clojure.string :as string]
           [seesaw.core :as ssw]
           )
  )

(defn popopen
  ""
  [title content]
  (let [fr (ssw/frame :title title, :content content, :on-close :exception)]
    (-> fr
        ssw/pack!
        ssw/show!))
   )

(defn window
  ""
  [title content]
  (ssw/frame :title title, :content content, :on-close :exception))

(defn update
  [fr kw newcontent]
  (ssw/config! fr kw newcontent))


(defn show
  ""
  [fr]
  (-> fr
      ssw/pack!
      ssw/show!))