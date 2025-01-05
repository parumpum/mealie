import { BaseCRUDAPI } from "../base/base-clients";
import {
  ChangePassword,
  DeleteTokenResponse,
  LongLiveTokenIn,
  LongLiveTokenOut,
  ResetPassword,
  UserBase,
  UserIn,
  UserOut,
  UserRatingOut,
  UserRatingSummary,
} from "~/lib/api/types/user";

export interface UserRatingsSummaries {
  ratings: UserRatingSummary[];
}

export interface UserRatingsOut {
  ratings: UserRatingOut[];
}

const prefix = "/api";

const routes = {
  usersSelf: `${prefix}/users/self`,
  ratingsSelf: `${prefix}/users/self/ratings`,
  householdBookmarksSelf: `${prefix}/users/self/household/bookmarks`,
  passwordReset: `${prefix}/users/reset-password`,
  passwordChange: `${prefix}/users/password`,
  users: `${prefix}/users`,

  usersIdImage: (id: string) => `${prefix}/users/${id}/image`,
  usersIdResetPassword: (id: string) => `${prefix}/users/${id}/reset-password`,
  usersId: (id: string) => `${prefix}/users/${id}`,
  usersIdBookmarks: (id: string) => `${prefix}/users/${id}/bookmarks`,
  usersIdBookmarksSlug: (id: string, slug: string) => `${prefix}/users/${id}/bookmarks/${slug}`,
  usersSelfBookmarksId: (id: string) => `${prefix}/users/self/bookmarks/${id}`,
  usersIdFavorites: (id: string) => `${prefix}/users/${id}/favorites`,
  usersIdFavoritesSlug: (id: string, slug: string) => `${prefix}/users/${id}/favorites/${slug}`,
  usersIdRatings: (id: string) => `${prefix}/users/${id}/ratings`,
  usersIdRatingsSlug: (id: string, slug: string) => `${prefix}/users/${id}/ratings/${slug}`,
  usersSelfFavoritesId: (id: string) => `${prefix}/users/self/favorites/${id}`,
  usersSelfRatingsId: (id: string) => `${prefix}/users/self/ratings/${id}`,

  usersApiTokens: `${prefix}/users/api-tokens`,
  usersApiTokensTokenId: (token_id: string | number) => `${prefix}/users/api-tokens/${token_id}`,

  householdBookmarksByRecipe: (id: string, slug: string) => `${prefix}/users/self/household/bookmarks/${slug}`

};

export class UserApi extends BaseCRUDAPI<UserIn, UserOut, UserBase> {
  baseRoute: string = routes.users;
  itemRoute = (itemid: string) => routes.usersId(itemid);

  async addBookmark(id: string, slug: string) {
    return await this.requests.post(routes.usersIdBookmarksSlug(id, slug), {});
  }

  async removeBookmark(id: string, slug: string) {
    return await this.requests.delete(routes.usersIdBookmarksSlug(id, slug));
  }

  async getHouseholdBookmarksByRecipe(id: string, slug: string) {
    return await this.requests.get<boolean>(routes.householdBookmarksByRecipe(id, slug));
  }

  async getHouseholdBookmarks() {
    return await this.requests.get<UserRatingsSummaries>(routes.householdBookmarksSelf);
  }

  async getBookmarks(id: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersIdBookmarks(id));
  }

  async getSelfBookmarks() {
    return await this.requests.get<UserRatingsSummaries>(routes.ratingsSelf);
  }

  async addFavorite(id: string, slug: string) {
    return await this.requests.post(routes.usersIdFavoritesSlug(id, slug), {});
  }

  async removeFavorite(id: string, slug: string) {
    return await this.requests.delete(routes.usersIdFavoritesSlug(id, slug));
  }

  async getFavorites(id: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersIdFavorites(id));
  }

  async getSelfFavorites() {
    return await this.requests.get<UserRatingsSummaries>(routes.ratingsSelf);
  }

  async getRatings(id: string) {
    return await this.requests.get<UserRatingsOut>(routes.usersIdRatings(id));
  }

  async setRating(id: string, slug: string, rating: number | null, isFavorite: boolean | null, isBookmarked: boolean | null) {
    return await this.requests.post(routes.usersIdRatingsSlug(id, slug), { rating, isFavorite, isBookmarked });
  }

  async getSelfRatings() {
    return await this.requests.get<UserRatingsSummaries>(routes.ratingsSelf);
  }

  async changePassword(changePassword: ChangePassword) {
    return await this.requests.put(routes.passwordChange, changePassword);
  }

  async createAPIToken(tokenName: LongLiveTokenIn) {
    return await this.requests.post<LongLiveTokenOut>(routes.usersApiTokens, tokenName);
  }

  async deleteAPIToken(tokenId: number) {
    return await this.requests.delete<DeleteTokenResponse>(routes.usersApiTokensTokenId(tokenId));
  }

  userProfileImage(id: string) {
    if (!id || id === undefined) return;
    return `/api/users/${id}/image`;
  }

  async resetPassword(payload: ResetPassword) {
    return await this.requests.post(routes.passwordReset, payload);
  }
}
